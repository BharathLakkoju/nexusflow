"""
Agent service: run individual agent executions outside of full workflow context.
"""
import logging
import time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import build_agent_graph, get_initial_state
from app.models.models import Agent, AgentExecution
from app.schemas.schemas import AgentRunRequest, AgentRunResponse
from app.services.analytics_service import record_event
from app.services.memory_service import get_memories_for_context
from app.services.rag_service import build_rag_context

logger = logging.getLogger(__name__)


async def run_agent(
    db: AsyncSession,
    org_id: str,
    agent_id: str,
    request: AgentRunRequest,
) -> AgentRunResponse:
    """Run a single agent and return the result."""
    # Load agent config
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.org_id == org_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise ValueError(f"Agent {agent_id} not found")

    model = request.model or agent.model or "openai/gpt-4o-mini"
    task = request.input

    # Create execution record
    execution = AgentExecution(
        agent_id=agent.id,
        org_id=org_id,
        status="running",
        input_data={"task": task},
    )
    db.add(execution)
    await db.flush()
    execution_id = str(execution.id)

    start_time = time.time()

    try:
        # Load context
        memory_ctx = await get_memories_for_context(db, org_id, task, top_k=3)
        rag_ctx = ""
        if agent.use_rag:
            rag_ctx = await build_rag_context(db, org_id, task, top_k=5)

        # Build and run graph
        available_agents = agent.agent_types or ["research", "planner", "executor", "critic"]
        compiled_graph = build_agent_graph(
            model=model,
            max_revisions=agent.max_revisions or 2,
            max_iterations=agent.max_iterations or 10,
            available_agents=available_agents,
        )

        initial_state = get_initial_state(
            task=task,
            org_id=org_id,
            execution_id=execution_id,
            model=model,
            max_revisions=agent.max_revisions or 2,
            max_iterations=agent.max_iterations or 10,
            memory_context=memory_ctx,
            rag_context=rag_ctx,
        )

        final_state = await compiled_graph.ainvoke(initial_state)

        output = final_state.get("draft") or final_state.get("final_output") or ""
        reasoning = final_state.get("reasoning_trace", [])
        latency_ms = int((time.time() - start_time) * 1000)

        execution.status = "completed"
        execution.output_data = {"output": output, "reasoning": reasoning}
        execution.latency_ms = latency_ms
        await db.flush()

        # Record analytics
        try:
            await record_event(
                db=db,
                org_id=org_id,
                event_type="agent_run",
                model=model,
                latency_ms=latency_ms,
                success=True,
                agent_type=agent.agent_type,
            )
        except Exception:
            pass

        await db.commit()

        return AgentRunResponse(
            execution_id=execution_id,
            output=output,
            reasoning_trace=reasoning,
            latency_ms=latency_ms,
            model=model,
        )

    except Exception as exc:
        latency_ms = int((time.time() - start_time) * 1000)
        execution.status = "failed"
        execution.error_message = str(exc)[:500]
        execution.latency_ms = latency_ms
        await db.commit()
        logger.error("[AgentService] Agent %s failed: %s", agent_id, exc)
        raise
