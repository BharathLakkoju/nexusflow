# Implements: F-010 (workflow execution), F-020 (multi-agent), F-035 (SSE streaming)
"""
Workflow engine: converts visual DAG JSON (nodes + edges) to executable LangGraph graphs.
Publishes SSE events to Upstash Redis for real-time streaming.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any, AsyncGenerator
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import build_agent_graph, get_initial_state
from app.config import settings
from app.db.database import get_db_context
from app.models.models import (
    ExecutionLog,
    HumanApproval,
    Workflow,
    WorkflowExecution,
)
from app.services.analytics_service import record_event
from app.services.memory_service import get_memories_for_context
from app.services.rag_service import build_rag_context

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SSE event helpers
# ---------------------------------------------------------------------------

async def push_event(execution_id: str, event: dict) -> None:
    """Push an SSE event to Upstash Redis list for streaming."""
    try:
        from upstash_redis import Redis

        redis = Redis(
            url=settings.UPSTASH_REDIS_REST_URL,
            token=settings.UPSTASH_REDIS_REST_TOKEN,
        )
        key = f"execution:events:{execution_id}"
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: redis.rpush(key, json.dumps(event)),
        )
        # Auto-expire after 1 hour
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: redis.expire(key, 3600),
        )
    except Exception as exc:
        logger.warning("[WorkflowEngine] Failed to push SSE event: %s", exc)


async def push_log_event(
    execution_id: str,
    node_id: str,
    node_type: str,
    event_type: str,
    data: dict,
) -> None:
    """Structured SSE log event."""
    await push_event(
        execution_id,
        {
            "type": event_type,
            "node_id": node_id,
            "node_type": node_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        },
    )


# ---------------------------------------------------------------------------
# Node executors
# ---------------------------------------------------------------------------

async def execute_agent_node(
    node: dict,
    context: dict,
    db: AsyncSession,
    execution_id: str,
) -> dict:
    """Execute an agent node using the multi-agent LangGraph graph."""
    node_id = node["id"]
    node_data = node.get("data", {})
    agent_type = node_data.get("agentType", "executor")
    model = node_data.get("model", settings.DEFAULT_MODEL)
    task = _resolve_template(node_data.get("prompt", context.get("input", "")), context)
    org_id = context["org_id"]

    await push_log_event(execution_id, node_id, "agent", "node_start", {
        "agent_type": agent_type,
        "model": model,
        "task_preview": task[:200],
    })

    start_time = time.time()

    # Pre-load memory and RAG context
    memory_ctx = ""
    rag_ctx = ""
    try:
        memory_ctx = await get_memories_for_context(db, org_id, task, top_k=3)
    except Exception:
        pass

    if node_data.get("useRag", False):
        try:
            rag_ctx = await build_rag_context(db, org_id, task, top_k=5)
        except Exception:
            pass

    # Determine which agents to use
    available_agents = _get_agent_types_for_node(agent_type, node_data)

    # Build and run graph
    compiled_graph = build_agent_graph(
        model=model,
        max_revisions=node_data.get("maxRevisions", 2),
        max_iterations=node_data.get("maxIterations", 10),
        available_agents=available_agents,
    )

    initial_state = get_initial_state(
        task=task,
        org_id=org_id,
        execution_id=execution_id,
        model=model,
        max_revisions=node_data.get("maxRevisions", 2),
        max_iterations=node_data.get("maxIterations", 10),
        memory_context=memory_ctx,
        rag_context=rag_ctx,
    )

    # Stream events from graph execution
    final_state = None
    async for event in compiled_graph.astream_events(initial_state, version="v1"):
        if event["event"] == "on_chain_end" and event["name"] in available_agents:
            agent_name = event["name"]
            output_state = event.get("data", {}).get("output", {})
            await push_log_event(execution_id, node_id, "agent", "agent_step", {
                "agent": agent_name,
                "output_preview": str(output_state.get("draft") or output_state.get("plan") or "")[:300],
            })
        if event["event"] == "on_chain_end" and event["name"] == "LangGraph":
            final_state = event.get("data", {}).get("output", {})

    if not final_state:
        # Fallback: invoke without streaming
        final_state = await compiled_graph.ainvoke(initial_state)

    latency_ms = int((time.time() - start_time) * 1000)
    output = final_state.get("draft") or final_state.get("final_output") or ""
    reasoning = final_state.get("reasoning_trace", [])

    await push_log_event(execution_id, node_id, "agent", "node_complete", {
        "output_preview": output[:500],
        "latency_ms": latency_ms,
        "iterations": final_state.get("iteration_count", 0),
    })

    # Log to DB
    db.add(ExecutionLog(
        execution_id=execution_id,
        node_id=node_id,
        node_type="agent",
        input_data={"task": task},
        output_data={"output": output, "reasoning": reasoning},
        latency_ms=latency_ms,
        success=True,
    ))
    await db.flush()

    return {"output": output, "reasoning": reasoning}


async def execute_tool_node(
    node: dict,
    context: dict,
    db: AsyncSession,
    execution_id: str,
) -> dict:
    """Execute a tool node."""
    from app.services.tool_service import execute_tool
    from app.schemas.schemas import ToolExecuteRequest

    node_id = node["id"]
    node_data = node.get("data", {})
    tool_name = node_data.get("toolName", "web_search")
    tool_input_raw = node_data.get("toolInput", {})

    # Resolve template variables
    tool_input = {}
    for k, v in tool_input_raw.items():
        tool_input[k] = _resolve_template(str(v), context) if isinstance(v, str) else v

    await push_log_event(execution_id, node_id, "tool", "node_start", {"tool": tool_name, "input": tool_input})

    result = await execute_tool(
        tool_name=tool_name,
        request=ToolExecuteRequest(
            tool_name=tool_name,
            input=tool_input,
            org_id=context.get("org_id"),
        ),
    )

    await push_log_event(execution_id, node_id, "tool", "node_complete", {
        "success": result.success,
        "latency_ms": result.latency_ms,
        "output_preview": str(result.output)[:300] if result.output else result.error,
    })

    db.add(ExecutionLog(
        execution_id=execution_id,
        node_id=node_id,
        node_type="tool",
        input_data=tool_input,
        output_data={"output": result.output, "error": result.error},
        latency_ms=result.latency_ms,
        success=result.success,
    ))
    await db.flush()

    return {"output": result.output, "error": result.error, "success": result.success}


async def execute_rag_node(
    node: dict,
    context: dict,
    db: AsyncSession,
    execution_id: str,
) -> dict:
    """Execute a RAG retrieval node."""
    node_id = node["id"]
    node_data = node.get("data", {})
    query = _resolve_template(node_data.get("query", context.get("input", "")), context)
    top_k = node_data.get("topK", 5)

    await push_log_event(execution_id, node_id, "rag", "node_start", {"query": query[:200]})

    rag_context = await build_rag_context(
        db=db,
        org_id=context["org_id"],
        query=query,
        top_k=top_k,
    )

    await push_log_event(execution_id, node_id, "rag", "node_complete", {
        "context_length": len(rag_context),
    })

    return {"output": rag_context, "rag_context": rag_context}


async def execute_memory_node(
    node: dict,
    context: dict,
    db: AsyncSession,
    execution_id: str,
) -> dict:
    """Execute a memory retrieval node."""
    from app.services.memory_service import get_memories_for_context, store_memory

    node_id = node["id"]
    node_data = node.get("data", {})
    action = node_data.get("action", "retrieve")  # "retrieve" or "store"
    query = _resolve_template(node_data.get("query", context.get("input", "")), context)

    await push_log_event(execution_id, node_id, "memory", "node_start", {"action": action})

    if action == "store":
        content = _resolve_template(node_data.get("content", context.get("output", "")), context)
        await store_memory(
            db=db,
            org_id=context["org_id"],
            content=content,
            memory_type=node_data.get("memoryType", "working"),
        )
        output = f"Stored memory: {content[:100]}"
    else:
        output = await get_memories_for_context(db, context["org_id"], query)

    await push_log_event(execution_id, node_id, "memory", "node_complete", {"output_len": len(output)})
    return {"output": output}


async def execute_conditional_node(
    node: dict,
    context: dict,
    execution_id: str,
) -> dict:
    """Evaluate a conditional expression to determine next path."""
    node_id = node["id"]
    node_data = node.get("data", {})
    condition = node_data.get("condition", "true")
    resolved = _resolve_template(condition, context)

    try:
        # Safe evaluation — only compare strings/numbers
        result = _safe_eval_condition(resolved, context)
    except Exception:
        result = bool(resolved.strip().lower() not in ("false", "0", "no", ""))

    await push_log_event(execution_id, node_id, "conditional", "node_complete", {
        "condition": condition,
        "result": result,
    })
    return {"output": str(result), "condition_result": result}


async def execute_human_approval_node(
    node: dict,
    context: dict,
    db: AsyncSession,
    execution_id: str,
) -> dict:
    """Pause execution and wait for human approval (timeout: 24h)."""
    node_id = node["id"]
    node_data = node.get("data", {})
    message = _resolve_template(node_data.get("message", "Approval required"), context)
    timeout_hours = node_data.get("timeoutHours", 24)

    # Create approval record
    approval = HumanApproval(
        execution_id=execution_id,
        node_id=node_id,
        org_id=context["org_id"],
        message=message,
        context_data={"execution_context": {k: str(v)[:200] for k, v in context.items()}},
        status="pending",
    )
    db.add(approval)
    await db.flush()

    await push_log_event(execution_id, node_id, "human_approval", "node_waiting", {
        "approval_id": str(approval.id),
        "message": message,
    })

    # Poll for approval (max timeout_hours * 3600 seconds, check every 10s)
    poll_interval = 10
    max_polls = (timeout_hours * 3600) // poll_interval

    for _ in range(max_polls):
        await asyncio.sleep(poll_interval)
        await db.refresh(approval)
        if approval.status == "approved":
            await push_log_event(execution_id, node_id, "human_approval", "node_complete", {
                "decision": "approved",
                "comment": approval.response_comment,
            })
            return {"output": "approved", "approved": True}
        elif approval.status == "rejected":
            await push_log_event(execution_id, node_id, "human_approval", "node_complete", {
                "decision": "rejected",
                "comment": approval.response_comment,
            })
            return {"output": "rejected", "approved": False}

    # Timeout
    approval.status = "timeout"
    await db.flush()
    return {"output": "timeout", "approved": False}


# ---------------------------------------------------------------------------
# DAG executor
# ---------------------------------------------------------------------------

async def execute_workflow(
    db: AsyncSession,
    workflow: Workflow,
    execution: WorkflowExecution,
    trigger_input: dict,
) -> None:
    """
    Execute a workflow DAG by traversing nodes in topological order.
    Updates execution status and pushes SSE events throughout.
    """
    execution_id = str(execution.id)
    org_id = str(workflow.org_id)

    nodes: list[dict] = workflow.nodes or []
    edges: list[dict] = workflow.edges or []

    await push_event(execution_id, {"type": "execution_start", "execution_id": execution_id})

    # Build adjacency map
    node_map = {n["id"]: n for n in nodes}
    children: dict[str, list[str]] = {n["id"]: [] for n in nodes}
    parents: dict[str, list[str]] = {n["id"]: [] for n in nodes}

    for edge in edges:
        src = edge.get("source", "")
        tgt = edge.get("target", "")
        if src in children:
            children[src].append(tgt)
        if tgt in parents:
            parents[tgt].append(src)

    # Topological sort (Kahn's algorithm)
    order = _topological_sort(nodes, edges)
    if not order:
        await _fail_execution(db, execution, "Workflow has no nodes or contains a cycle")
        return

    # Execution context: carries outputs between nodes
    context: dict[str, Any] = {
        "input": trigger_input.get("input", ""),
        "org_id": org_id,
        "execution_id": execution_id,
        **trigger_input,
    }
    # Per-node outputs
    node_outputs: dict[str, Any] = {}

    execution.status = "running"
    execution.started_at = datetime.now(timezone.utc)
    await db.flush()

    total_tokens_input = 0
    total_tokens_output = 0

    try:
        for node_id in order:
            node = node_map.get(node_id)
            if not node:
                continue

            node_type = node.get("type", "")

            # Merge upstream outputs into context
            for parent_id in parents.get(node_id, []):
                parent_out = node_outputs.get(parent_id, {})
                if isinstance(parent_out, dict):
                    # Namespace by node_id to avoid collisions
                    context[f"node_{parent_id}_output"] = parent_out.get("output", "")
                    # Also set generic 'output' from most recent parent
                    if parent_out.get("output"):
                        context["output"] = parent_out["output"]

            # Execute node
            try:
                if node_type == "start":
                    node_outputs[node_id] = {"output": context.get("input", "")}
                elif node_type == "end":
                    node_outputs[node_id] = {"output": context.get("output", "")}
                    await push_event(execution_id, {
                        "type": "final_output",
                        "output": context.get("output", ""),
                    })
                elif node_type == "agent":
                    result = await execute_agent_node(node, context, db, execution_id)
                    node_outputs[node_id] = result
                    context["output"] = result.get("output", "")
                elif node_type == "tool":
                    result = await execute_tool_node(node, context, db, execution_id)
                    node_outputs[node_id] = result
                    if result.get("output"):
                        context["output"] = str(result["output"])
                elif node_type == "rag":
                    result = await execute_rag_node(node, context, db, execution_id)
                    node_outputs[node_id] = result
                    context["rag_context"] = result.get("rag_context", "")
                elif node_type == "memory":
                    result = await execute_memory_node(node, context, db, execution_id)
                    node_outputs[node_id] = result
                    context["memory_context"] = result.get("output", "")
                elif node_type == "conditional":
                    result = await execute_conditional_node(node, context, execution_id)
                    node_outputs[node_id] = result
                    context["condition_result"] = result.get("condition_result", False)
                elif node_type == "human_approval":
                    result = await execute_human_approval_node(node, context, db, execution_id)
                    node_outputs[node_id] = result
                    if not result.get("approved", True):
                        await _complete_execution(db, execution, "rejected", context.get("output", ""), 0, 0)
                        await push_event(execution_id, {"type": "execution_rejected"})
                        return
                elif node_type in ("webhook", "scheduler"):
                    node_outputs[node_id] = {"output": json.dumps(trigger_input)}
                else:
                    logger.warning("[WorkflowEngine] Unknown node type: %s", node_type)
                    node_outputs[node_id] = {}
            except Exception as node_exc:
                logger.error("[WorkflowEngine] Node %s failed: %s", node_id, node_exc)
                await push_log_event(execution_id, node_id, node_type, "node_error", {"error": str(node_exc)})
                db.add(ExecutionLog(
                    execution_id=execution_id,
                    node_id=node_id,
                    node_type=node_type,
                    input_data={},
                    output_data={"error": str(node_exc)},
                    success=False,
                    error_message=str(node_exc)[:500],
                ))
                await db.flush()
                # Continue to next nodes (graceful degradation)
                node_outputs[node_id] = {"output": "", "error": str(node_exc)}

        # Workflow completed
        final_output = context.get("output", "")
        await _complete_execution(db, execution, "completed", final_output, total_tokens_input, total_tokens_output)
        await push_event(execution_id, {
            "type": "execution_complete",
            "status": "completed",
            "output": final_output[:2000],
        })

    except Exception as exc:
        logger.error("[WorkflowEngine] Workflow %s failed: %s", execution_id, exc)
        await _fail_execution(db, execution, str(exc)[:500])
        await push_event(execution_id, {"type": "execution_failed", "error": str(exc)[:500]})

    finally:
        await db.commit()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _topological_sort(nodes: list[dict], edges: list[dict]) -> list[str]:
    """Kahn's algorithm for topological sort of DAG nodes."""
    from collections import deque

    node_ids = [n["id"] for n in nodes]
    in_degree = {nid: 0 for nid in node_ids}
    adj: dict[str, list[str]] = {nid: [] for nid in node_ids}

    for edge in edges:
        src = edge.get("source", "")
        tgt = edge.get("target", "")
        if src in adj and tgt in in_degree:
            adj[src].append(tgt)
            in_degree[tgt] += 1

    queue = deque([nid for nid in node_ids if in_degree[nid] == 0])
    order = []

    while queue:
        nid = queue.popleft()
        order.append(nid)
        for neighbor in adj[nid]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order if len(order) == len(node_ids) else order  # Return partial on cycle


def _resolve_template(template: str, context: dict) -> str:
    """Resolve {{variable}} placeholders using the execution context."""
    import re

    def replace(match):
        key = match.group(1).strip()
        return str(context.get(key, f"{{{{{key}}}}}"))

    return re.sub(r"\{\{(\w+)\}\}", replace, template)


def _safe_eval_condition(expr: str, context: dict) -> bool:
    """Very limited safe condition evaluator. Only handles simple comparisons."""
    expr = expr.strip()
    # Boolean literals
    if expr.lower() == "true":
        return True
    if expr.lower() == "false":
        return False
    # Contains check
    if " contains " in expr.lower():
        parts = expr.lower().split(" contains ")
        return parts[1].strip().strip("\"'") in parts[0].strip().lower()
    # Equality
    if "==" in expr:
        left, right = expr.split("==", 1)
        return left.strip().strip("\"'") == right.strip().strip("\"'")
    # Inequality
    if "!=" in expr:
        left, right = expr.split("!=", 1)
        return left.strip().strip("\"'") != right.strip().strip("\"'")
    # Non-empty check
    return bool(expr)


async def _complete_execution(
    db: AsyncSession,
    execution: WorkflowExecution,
    status: str,
    output: str,
    tokens_input: int,
    tokens_output: int,
) -> None:
    execution.status = status
    execution.completed_at = datetime.now(timezone.utc)
    execution.output = output[:10000] if output else None
    execution.tokens_input = tokens_input
    execution.tokens_output = tokens_output
    await db.flush()


async def _fail_execution(db: AsyncSession, execution: WorkflowExecution, error: str) -> None:
    execution.status = "failed"
    execution.completed_at = datetime.now(timezone.utc)
    execution.error_message = error
    await db.flush()
