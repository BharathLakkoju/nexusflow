# Implements: F-037 (document ingestion job), F-038 (workflow background execution)
"""
Inngest functions: background jobs for document ingestion and workflow execution.
"""
from __future__ import annotations

import inngest

from app.inngest.client import inngest_client


@inngest_client.create_function(
    fn_id="ingest-document",
    trigger=inngest.TriggerEvent(event="nexusflow/document.ingest"),
    retries=3,
)
async def ingest_document_fn(ctx: inngest.Context, step: inngest.Step) -> dict:
    """Background function: process and embed an uploaded document."""
    document_id = ctx.event.data.get("document_id")
    if not document_id:
        raise ValueError("document_id is required in event data")

    async def _do_ingest():
        from app.db.database import get_db_context
        from app.services.ingestion_service import ingest_document

        async with get_db_context() as db:
            return await ingest_document(db, document_id)

    result = await step.run("ingest-and-embed", _do_ingest)
    return result


@inngest_client.create_function(
    fn_id="run-workflow",
    trigger=inngest.TriggerEvent(event="nexusflow/workflow.run"),
    retries=2,
    concurrency=[inngest.Concurrency(limit=5)],
)
async def run_workflow_fn(ctx: inngest.Context, step: inngest.Step) -> dict:
    """Background function: execute a workflow DAG asynchronously."""
    execution_id = ctx.event.data.get("execution_id")
    workflow_id = ctx.event.data.get("workflow_id")
    trigger_input = ctx.event.data.get("trigger_input", {})

    if not execution_id or not workflow_id:
        raise ValueError("execution_id and workflow_id are required")

    async def _do_execute():
        from sqlalchemy import select

        from app.db.database import get_db_context
        from app.models.models import Workflow, WorkflowExecution
        from app.services.workflow_engine import execute_workflow

        async with get_db_context() as db:
            wf_result = await db.execute(
                select(Workflow).where(Workflow.id == workflow_id)
            )
            workflow = wf_result.scalar_one()

            exec_result = await db.execute(
                select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            )
            execution = exec_result.scalar_one()

            await execute_workflow(
                db=db,
                workflow=workflow,
                execution=execution,
                trigger_input=trigger_input,
            )

        return {"status": "completed", "execution_id": execution_id}

    result = await step.run("execute-workflow-dag", _do_execute)
    return result


# List of all Inngest functions (used in main.py to serve the Inngest endpoint)
INNGEST_FUNCTIONS = [ingest_document_fn, run_workflow_fn]
