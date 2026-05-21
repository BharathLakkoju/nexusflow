"""
Analytics service: aggregates execution metrics for the dashboard.
"""
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AnalyticsEvent, WorkflowExecution, Workflow
from app.schemas.schemas import AnalyticsDashboard

logger = logging.getLogger(__name__)

# OpenRouter model pricing (cost per 1M tokens) — updated May 2026
MODEL_PRICING: dict[str, dict[str, float]] = {
    "openai/gpt-4o": {"input": 5.0, "output": 15.0},
    "openai/gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "openai/gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "anthropic/claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
    "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
    "google/gemini-2.0-flash": {"input": 0.075, "output": 0.30},
    "meta-llama/llama-3.1-8b-instruct": {"input": 0.06, "output": 0.06},
    "deepseek/deepseek-chat": {"input": 0.14, "output": 0.28},
}


def estimate_cost(model: str, tokens_input: int, tokens_output: int) -> Decimal:
    """Estimate cost in USD given model and token counts."""
    pricing = MODEL_PRICING.get(model, {"input": 1.0, "output": 3.0})
    cost = (tokens_input / 1_000_000) * pricing["input"] + (tokens_output / 1_000_000) * pricing["output"]
    return Decimal(str(round(cost, 8)))


async def record_event(
    db: AsyncSession,
    org_id: str,
    event_type: str,
    model: str = "",
    tokens_input: int = 0,
    tokens_output: int = 0,
    latency_ms: int = 0,
    success: bool = True,
    workflow_id: str | None = None,
    execution_id: str | None = None,
    agent_type: str | None = None,
    metadata: dict | None = None,
) -> None:
    """Record an analytics event. Fire-and-forget safe."""
    cost = estimate_cost(model, tokens_input, tokens_output) if model else Decimal("0")
    event = AnalyticsEvent(
        org_id=org_id,
        event_type=event_type,
        workflow_id=workflow_id,
        execution_id=execution_id,
        agent_type=agent_type,
        model=model or None,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        cost_estimate=cost,
        latency_ms=latency_ms,
        success=success,
        event_metadata=metadata or {},
    )
    db.add(event)
    await db.flush()  # Don't commit here; caller commits


async def get_dashboard(
    db: AsyncSession,
    org_id: str,
    days: int = 30,
) -> AnalyticsDashboard:
    """Build the analytics dashboard for an organization."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    since_str = since.isoformat()

    # Total executions
    exec_counts = await db.execute(
        text("""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE status = 'completed') AS successful,
                COUNT(*) FILTER (WHERE status = 'failed') AS failed
            FROM workflow_executions
            WHERE org_id = :org_id AND created_at >= :since
        """),
        {"org_id": org_id, "since": since},
    )
    counts_row = exec_counts.one()

    # Active workflows
    active_wf = await db.execute(
        text("SELECT COUNT(*) FROM workflows WHERE org_id = :org_id AND status = 'active'"),
        {"org_id": org_id},
    )
    active_count = active_wf.scalar_one()

    # Token & cost totals
    token_totals = await db.execute(
        text("""
            SELECT
                COALESCE(SUM(tokens_input + tokens_output), 0) AS total_tokens,
                COALESCE(SUM(cost_estimate), 0) AS total_cost,
                AVG(latency_ms) AS avg_latency
            FROM analytics_events
            WHERE org_id = :org_id AND created_at >= :since
        """),
        {"org_id": org_id, "since": since},
    )
    token_row = token_totals.one()

    # Executions by day
    daily_execs = await db.execute(
        text("""
            SELECT
                DATE(created_at) AS day,
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE status = 'completed') AS successful
            FROM workflow_executions
            WHERE org_id = :org_id AND created_at >= :since
            GROUP BY day ORDER BY day
        """),
        {"org_id": org_id, "since": since},
    )
    executions_by_day = [
        {"day": str(r.day), "total": r.total, "successful": r.successful}
        for r in daily_execs
    ]

    # Token usage by model
    model_usage = await db.execute(
        text("""
            SELECT
                COALESCE(model, 'unknown') AS model,
                SUM(tokens_input + tokens_output) AS tokens,
                SUM(cost_estimate) AS cost
            FROM analytics_events
            WHERE org_id = :org_id AND created_at >= :since AND model IS NOT NULL
            GROUP BY model ORDER BY tokens DESC LIMIT 10
        """),
        {"org_id": org_id, "since": since},
    )
    token_by_model = [
        {"model": r.model, "tokens": int(r.tokens or 0), "cost": float(r.cost or 0)}
        for r in model_usage
    ]

    # Top workflows by execution count
    top_wf = await db.execute(
        text("""
            SELECT
                we.workflow_id,
                w.name AS workflow_name,
                COUNT(*) AS executions,
                COUNT(*) FILTER (WHERE we.status = 'completed') AS successful
            FROM workflow_executions we
            LEFT JOIN workflows w ON we.workflow_id = w.id
            WHERE we.org_id = :org_id AND we.created_at >= :since
              AND we.workflow_id IS NOT NULL
            GROUP BY we.workflow_id, w.name
            ORDER BY executions DESC LIMIT 10
        """),
        {"org_id": org_id, "since": since},
    )
    top_workflows = [
        {
            "workflow_id": str(r.workflow_id),
            "name": r.workflow_name or "Deleted Workflow",
            "executions": r.executions,
            "successful": r.successful,
        }
        for r in top_wf
    ]

    # Agent performance
    agent_perf = await db.execute(
        text("""
            SELECT
                agent_type,
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE success) AS successful,
                AVG(latency_ms) AS avg_latency,
                SUM(tokens_input + tokens_output) AS total_tokens
            FROM analytics_events
            WHERE org_id = :org_id AND created_at >= :since AND agent_type IS NOT NULL
            GROUP BY agent_type ORDER BY total DESC
        """),
        {"org_id": org_id, "since": since},
    )
    agent_performance = [
        {
            "agent_type": r.agent_type,
            "total": r.total,
            "successful": r.successful,
            "success_rate": round((r.successful / r.total) * 100, 1) if r.total else 0,
            "avg_latency_ms": round(float(r.avg_latency or 0)),
            "total_tokens": int(r.total_tokens or 0),
        }
        for r in agent_perf
    ]

    # Cost by day
    daily_cost = await db.execute(
        text("""
            SELECT
                DATE(created_at) AS day,
                SUM(cost_estimate) AS cost
            FROM analytics_events
            WHERE org_id = :org_id AND created_at >= :since
            GROUP BY day ORDER BY day
        """),
        {"org_id": org_id, "since": since},
    )
    cost_by_day = [
        {"day": str(r.day), "cost": float(r.cost or 0)}
        for r in daily_cost
    ]

    return AnalyticsDashboard(
        total_executions=counts_row.total,
        successful_executions=counts_row.successful,
        failed_executions=counts_row.failed,
        active_workflows=active_count,
        total_tokens=int(token_row.total_tokens or 0),
        total_cost=Decimal(str(token_row.total_cost or 0)),
        avg_latency_ms=float(token_row.avg_latency) if token_row.avg_latency else None,
        executions_by_day=executions_by_day,
        token_usage_by_model=token_by_model,
        top_workflows=top_workflows,
        agent_performance=agent_performance,
        cost_by_day=cost_by_day,
    )
