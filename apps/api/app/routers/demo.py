"""
Demo seed router — POST /demo/seed
Inserts sample workflows, agents, documents, and memory entries for the
authenticated user's organisation if none exist yet.
Idempotent: safe to call multiple times.
"""
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.middleware.auth import UserInfo
from app.middleware.rbac import RequireMember
from app.models.models import (
    Agent,
    AnalyticsEvent,
    Document,
    HumanApproval,
    Memory,
    Workflow,
    WorkflowExecution,
)

router = APIRouter(prefix="/demo", tags=["demo"])

# ---------------------------------------------------------------------------
# Seed data definitions
# ---------------------------------------------------------------------------

def _demo_workflows(org_id: uuid.UUID, user_id: str) -> list[dict[str, Any]]:
    return [
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "name": "Customer Support Bot",
            "description": "Automated customer support with human escalation for complex issues",
            "status": "active",
            "trigger_type": "manual",
            "version": 3,
            "is_template": False,
            "nodes": [
                {"id": "start", "type": "start", "position": {"x": 50, "y": 200}, "data": {"label": "Start"}},
                {"id": "agent-1", "type": "agent", "position": {"x": 250, "y": 200}, "data": {
                    "label": "Support Agent",
                    "model": "meta-llama/llama-3.3-70b-instruct:free",
                    "system_prompt": "You are a helpful customer support agent. Resolve issues politely.",
                }},
                {"id": "condition-1", "type": "condition", "position": {"x": 450, "y": 200}, "data": {
                    "label": "Needs escalation?", "condition": "confidence < 0.7",
                }},
                {"id": "approval-1", "type": "human_approval", "position": {"x": 650, "y": 100}, "data": {
                    "label": "Human Review", "message": "Please review this customer case",
                }},
                {"id": "end", "type": "end", "position": {"x": 850, "y": 200}, "data": {"label": "End"}},
            ],
            "edges": [
                {"id": "e1", "source": "start", "target": "agent-1"},
                {"id": "e2", "source": "agent-1", "target": "condition-1"},
                {"id": "e3", "source": "condition-1", "target": "approval-1", "type": "true"},
                {"id": "e4", "source": "condition-1", "target": "end", "type": "false"},
                {"id": "e5", "source": "approval-1", "target": "end"},
            ],
            "trigger_config": {},
            "created_by": user_id,
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "name": "Research & Summarize",
            "description": "Search the web, retrieve relevant documents, and synthesise a concise summary",
            "status": "active",
            "trigger_type": "manual",
            "version": 2,
            "is_template": False,
            "nodes": [
                {"id": "start", "type": "start", "position": {"x": 50, "y": 200}, "data": {"label": "Start"}},
                {"id": "rag-1", "type": "rag", "position": {"x": 250, "y": 200}, "data": {
                    "label": "Knowledge Base Lookup", "top_k": 5,
                }},
                {"id": "tool-1", "type": "tool", "position": {"x": 450, "y": 100}, "data": {
                    "label": "Web Search", "tool_name": "web_search",
                }},
                {"id": "agent-1", "type": "agent", "position": {"x": 650, "y": 200}, "data": {
                    "label": "Research Agent",
                    "model": "deepseek/deepseek-r1:free",
                    "system_prompt": "Synthesise the provided context into a clear, concise summary with citations.",
                }},
                {"id": "end", "type": "end", "position": {"x": 850, "y": 200}, "data": {"label": "End"}},
            ],
            "edges": [
                {"id": "e1", "source": "start", "target": "rag-1"},
                {"id": "e2", "source": "rag-1", "target": "tool-1"},
                {"id": "e3", "source": "tool-1", "target": "agent-1"},
                {"id": "e4", "source": "agent-1", "target": "end"},
            ],
            "trigger_config": {},
            "created_by": user_id,
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "name": "Daily Report Generator",
            "description": "Scheduled workflow that pulls data, analyses trends, and stores a summary",
            "status": "active",
            "trigger_type": "schedule",
            "version": 1,
            "is_template": False,
            "nodes": [
                {"id": "start", "type": "start", "position": {"x": 50, "y": 200}, "data": {
                    "label": "Daily Trigger", "cron": "0 9 * * 1-5",
                }},
                {"id": "tool-1", "type": "tool", "position": {"x": 250, "y": 200}, "data": {
                    "label": "Fetch Metrics", "tool_name": "http_request",
                }},
                {"id": "agent-1", "type": "agent", "position": {"x": 450, "y": 200}, "data": {
                    "label": "Analyst Agent",
                    "model": "qwen/qwen3-235b-a22b:free",
                    "system_prompt": "Analyse the provided metrics and generate a concise executive summary.",
                }},
                {"id": "memory-1", "type": "memory", "position": {"x": 650, "y": 200}, "data": {
                    "label": "Store to Memory", "memory_type": "long_term",
                }},
                {"id": "end", "type": "end", "position": {"x": 850, "y": 200}, "data": {"label": "End"}},
            ],
            "edges": [
                {"id": "e1", "source": "start", "target": "tool-1"},
                {"id": "e2", "source": "tool-1", "target": "agent-1"},
                {"id": "e3", "source": "agent-1", "target": "memory-1"},
                {"id": "e4", "source": "memory-1", "target": "end"},
            ],
            "trigger_config": {"cron": "0 9 * * 1-5"},
            "created_by": user_id,
        },
    ]


def _demo_agents(org_id: uuid.UUID, user_id: str) -> list[dict[str, Any]]:
    return [
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "name": "Research Agent",
            "type": "research",
            "description": "Searches the web and knowledge base to answer complex research questions",
            "system_prompt": "You are an expert research assistant. Search the web and internal knowledge base to provide accurate, cited answers.",
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "temperature": Decimal("0.70"),
            "max_tokens": 4000,
            "tools": ["web_search", "rag_search"],
            "config": {},
            "created_by": user_id,
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "name": "Code Review Agent",
            "type": "executor",
            "description": "Reviews code for bugs, security issues, and style violations",
            "system_prompt": "You are a senior software engineer. Review code carefully for bugs, security vulnerabilities, and best practices.",
            "model": "deepseek/deepseek-r1:free",
            "temperature": Decimal("0.30"),
            "max_tokens": 4000,
            "tools": ["code_executor"],
            "config": {},
            "created_by": user_id,
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "name": "Customer Support Agent",
            "type": "supervisor",
            "description": "Handles customer inquiries and routes escalations appropriately",
            "system_prompt": "You are a friendly, professional customer support representative. Resolve issues with empathy and clarity.",
            "model": "google/gemma-3-27b-it:free",
            "temperature": Decimal("0.70"),
            "max_tokens": 2000,
            "tools": ["web_search"],
            "config": {},
            "created_by": user_id,
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "name": "Data Analyst Agent",
            "type": "research",
            "description": "Interprets datasets, generates insights, and produces structured reports",
            "system_prompt": "You are a data analyst. Interpret provided data, identify trends, and produce clear, actionable reports.",
            "model": "qwen/qwen3-235b-a22b:free",
            "temperature": Decimal("0.50"),
            "max_tokens": 4000,
            "tools": ["code_executor", "http_request"],
            "config": {},
            "created_by": user_id,
        },
    ]


def _demo_documents(org_id: uuid.UUID, user_id: str) -> list[dict[str, Any]]:
    return [
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "name": "NexusFlow Product Guide.pdf",
            "file_type": "pdf",
            "file_url": "https://placeholder.nexusflow.ai/demo/product-guide.pdf",
            "file_size": 2457600,
            "status": "completed",
            "chunk_count": 142,
            "error_message": None,
            "doc_metadata": {"demo": True},
            "created_by": user_id,
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "name": "API Integration Handbook.md",
            "file_type": "markdown",
            "file_url": "https://placeholder.nexusflow.ai/demo/api-handbook.md",
            "file_size": 81920,
            "status": "completed",
            "chunk_count": 38,
            "error_message": None,
            "doc_metadata": {"demo": True},
            "created_by": user_id,
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "name": "Customer FAQ Database.txt",
            "file_type": "txt",
            "file_url": "https://placeholder.nexusflow.ai/demo/faq.txt",
            "file_size": 163840,
            "status": "completed",
            "chunk_count": 67,
            "error_message": None,
            "doc_metadata": {"demo": True},
            "created_by": user_id,
        },
    ]


def _demo_memories(org_id: uuid.UUID) -> list[dict[str, Any]]:
    return [
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "agent_id": None,
            "execution_id": None,
            "memory_type": "short_term",
            "content": "User requested analysis of Q4 sales data. Focus areas: APAC growth, churn rate reduction, and new product uptake.",
            "embedding": None,
            "relevance_score": None,
            "mem_metadata": {"demo": True},
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "agent_id": None,
            "execution_id": None,
            "memory_type": "long_term",
            "content": "Customer prefers concise bullet-point summaries over long prose. Always include a TL;DR at the top.",
            "embedding": None,
            "relevance_score": None,
            "mem_metadata": {"demo": True},
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "agent_id": None,
            "execution_id": None,
            "memory_type": "episodic",
            "content": "Successfully resolved payment gateway integration issue on 2024-11-14. Root cause: API key rotation without secret manager update.",
            "embedding": None,
            "relevance_score": None,
            "mem_metadata": {"demo": True},
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "agent_id": None,
            "execution_id": None,
            "memory_type": "long_term",
            "content": "Project milestone: NexusFlow v2.0 public launch scheduled for Q1 2025. Key deliverables: multi-tenant RBAC, streaming execution, marketplace integrations.",
            "embedding": None,
            "relevance_score": None,
            "mem_metadata": {"demo": True},
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "agent_id": None,
            "execution_id": None,
            "memory_type": "short_term",
            "content": "Current task: Generate weekly performance report for the executive team. KPIs: DAU, retention rate, revenue, and NPS.",
            "embedding": None,
            "relevance_score": None,
            "mem_metadata": {"demo": True},
        },
    ]


def _demo_activity(
    org_id: uuid.UUID,
    user_id: str,
    workflow_ids: list[uuid.UUID],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    now = datetime.now(timezone.utc)
    exec_id_1 = uuid.uuid4()
    exec_id_2 = uuid.uuid4()
    exec_id_3 = uuid.uuid4()
    exec_id_4 = uuid.uuid4()

    support_wf = workflow_ids[0]
    research_wf = workflow_ids[1]
    report_wf = workflow_ids[2]

    executions = [
        {
            "id": exec_id_1,
            "workflow_id": support_wf,
            "org_id": org_id,
            "status": "completed",
            "input": {"ticket": "Customer cannot access billing portal"},
            "output": {"summary": "Resolved by refreshing account permissions"},
            "error": None,
            "started_at": now - timedelta(days=3, minutes=8),
            "completed_at": now - timedelta(days=3),
            "total_tokens": 3120,
            "estimated_cost": Decimal("0.00000000"),
            "triggered_by": user_id,
        },
        {
            "id": exec_id_2,
            "workflow_id": research_wf,
            "org_id": org_id,
            "status": "completed",
            "input": {"topic": "AI procurement risk controls"},
            "output": {"summary": "Generated a sourced research brief"},
            "error": None,
            "started_at": now - timedelta(days=2, minutes=11),
            "completed_at": now - timedelta(days=2),
            "total_tokens": 4680,
            "estimated_cost": Decimal("0.00000000"),
            "triggered_by": user_id,
        },
        {
            "id": exec_id_3,
            "workflow_id": report_wf,
            "org_id": org_id,
            "status": "failed",
            "input": {"report": "Weekly executive summary"},
            "output": None,
            "error": "Metrics API returned a 503 response",
            "started_at": now - timedelta(days=1, minutes=5),
            "completed_at": now - timedelta(days=1),
            "total_tokens": 1420,
            "estimated_cost": Decimal("0.00000000"),
            "triggered_by": user_id,
        },
        {
            "id": exec_id_4,
            "workflow_id": report_wf,
            "org_id": org_id,
            "status": "waiting_approval",
            "input": {"task": "Batch email report"},
            "output": None,
            "error": None,
            "started_at": now - timedelta(hours=4),
            "completed_at": None,
            "total_tokens": 890,
            "estimated_cost": Decimal("0.00000000"),
            "triggered_by": user_id,
        },
    ]

    approvals = [
        {
            "id": uuid.uuid4(),
            "execution_id": exec_id_4,
            "node_id": "approval-security",
            "status": "pending",
            "request_data": {
                "message": "Research Agent identified a critical security vulnerability in the authentication module. Proposed fix: patch JWT validation logic. Deploy to production?",
                "context": {
                    "workflow": "Customer Support Bot",
                    "node": "Security Review",
                    "risk_level": "high",
                    "suggested_action": "Apply patch to JWT middleware and redeploy API service.",
                },
            },
            "response_data": None,
            "approved_by": None,
        },
        {
            "id": uuid.uuid4(),
            "execution_id": exec_id_4,
            "node_id": "approval-batch",
            "status": "pending",
            "request_data": {
                "message": "Daily Report Generator is ready to send the weekly summary to 847 customer records via email. This action cannot be undone. Confirm batch send?",
                "context": {
                    "workflow": "Daily Report Generator",
                    "node": "Batch Email Sender",
                    "recipients": 847,
                    "template": "weekly_performance_summary_v3",
                },
            },
            "response_data": None,
            "approved_by": None,
        },
    ]

    events = [
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "event_type": "agent.run",
            "workflow_id": support_wf,
            "execution_id": exec_id_1,
            "agent_type": "supervisor",
            "model": "google/gemma-3-27b-it:free",
            "tokens_input": 1250,
            "tokens_output": 1870,
            "cost_estimate": Decimal("0.00000000"),
            "latency_ms": 1840,
            "success": True,
            "event_metadata": {"demo": True},
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "event_type": "agent.run",
            "workflow_id": research_wf,
            "execution_id": exec_id_2,
            "agent_type": "research",
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "tokens_input": 2110,
            "tokens_output": 2570,
            "cost_estimate": Decimal("0.00000000"),
            "latency_ms": 3260,
            "success": True,
            "event_metadata": {"demo": True},
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "event_type": "agent.run",
            "workflow_id": report_wf,
            "execution_id": exec_id_3,
            "agent_type": "research",
            "model": "qwen/qwen3-235b-a22b:free",
            "tokens_input": 780,
            "tokens_output": 640,
            "cost_estimate": Decimal("0.00000000"),
            "latency_ms": 2140,
            "success": False,
            "event_metadata": {"demo": True, "error": "Metrics API returned a 503 response"},
        },
        {
            "id": uuid.uuid4(),
            "org_id": org_id,
            "event_type": "agent.run",
            "workflow_id": report_wf,
            "execution_id": exec_id_4,
            "agent_type": "executor",
            "model": "deepseek/deepseek-r1:free",
            "tokens_input": 420,
            "tokens_output": 470,
            "cost_estimate": Decimal("0.00000000"),
            "latency_ms": 990,
            "success": True,
            "event_metadata": {"demo": True, "state": "waiting_approval"},
        },
    ]

    return executions, approvals, events


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/seed", status_code=200)
async def seed_demo_data(
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Seed demo workflows, agents, documents, memory, and approvals for the
    authenticated user's organisation. Safe to call multiple times — skips
    seeding if data already exists.
    """
    if not current_user.org_id:
        raise HTTPException(status_code=403, detail="No organization membership found")

    org_id = uuid.UUID(str(current_user.org_id))

    # --- Guard: skip if any workflows exist ---
    existing = await db.execute(
        select(func.count()).select_from(Workflow).where(Workflow.org_id == org_id)
    )
    count = existing.scalar_one()
    if count > 0:
        return {"seeded": False, "reason": "Organisation already has data"}

    user_id = current_user.user_id
    summary: dict[str, int] = {}

    # --- Workflows ---
    workflows = _demo_workflows(org_id, user_id)
    for w in workflows:
        db.add(Workflow(**w))
    summary["workflows"] = len(workflows)

    # --- Agents ---
    for a in _demo_agents(org_id, user_id):
        db.add(Agent(**a))
    summary["agents"] = 4

    # --- Documents ---
    for d in _demo_documents(org_id, user_id):
        db.add(Document(**d))
    summary["documents"] = 3

    # --- Memory ---
    for m in _demo_memories(org_id):
        db.add(Memory(**m))
    summary["memories"] = 5

    # --- Executions + Approvals ---
    workflow_ids = [w["id"] for w in workflows]
    executions, approvals, events = _demo_activity(org_id, user_id, workflow_ids)
    for e in executions:
        db.add(WorkflowExecution(**e))
    for ap in approvals:
        db.add(HumanApproval(**ap))
    for event in events:
        db.add(AnalyticsEvent(**event))
    summary["executions"] = len(executions)
    summary["approvals"] = len(approvals)
    summary["analytics_events"] = len(events)

    await db.commit()
    return {"seeded": True, "summary": summary}
