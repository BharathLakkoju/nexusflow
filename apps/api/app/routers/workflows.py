# Implements: F-005 (workflow CRUD), F-010 (workflow execution)
"""
Workflows router: CRUD + execution trigger.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.middleware.auth import UserInfo
from app.middleware.rbac import RequireMember, RequireViewer
from app.models.models import Workflow, WorkflowExecution, WorkflowVersion
from app.schemas.schemas import (
    ExecutionResponse,
    WorkflowCreate,
    WorkflowExecuteRequest,
    WorkflowResponse,
    WorkflowUpdate,
)

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    body: WorkflowCreate,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> WorkflowResponse:
    wf = Workflow(
        org_id=current_user.org_id,
        name=body.name,
        description=body.description,
        nodes=body.nodes or [],
        edges=body.edges or [],
        version=1,
        status="draft",
        trigger_type=body.trigger_type or "manual",
        trigger_config=body.trigger_config or {},
        created_by=current_user.user_id,
    )
    db.add(wf)
    await db.commit()
    await db.refresh(wf)
    return WorkflowResponse.model_validate(wf)


@router.get("", response_model=list[WorkflowResponse])
async def list_workflows(
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> list[WorkflowResponse]:
    result = await db.execute(
        select(Workflow).where(Workflow.org_id == current_user.org_id)
        .order_by(Workflow.updated_at.desc())
    )
    workflows = result.scalars().all()
    return [WorkflowResponse.model_validate(w) for w in workflows]


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: UUID,
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> WorkflowResponse:
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.org_id == current_user.org_id,
        )
    )
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowResponse.model_validate(wf)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    body: WorkflowUpdate,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> WorkflowResponse:
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.org_id == current_user.org_id,
        )
    )
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Save version snapshot before update
    version = WorkflowVersion(
        workflow_id=wf.id,
        version=wf.version,
        nodes=wf.nodes,
        edges=wf.edges,
        created_by=current_user.user_id,
    )
    db.add(version)

    if body.name is not None:
        wf.name = body.name
    if body.description is not None:
        wf.description = body.description
    if body.nodes is not None:
        wf.nodes = body.nodes
    if body.edges is not None:
        wf.edges = body.edges
    if body.status is not None:
        wf.status = body.status
    if body.trigger_type is not None:
        wf.trigger_type = body.trigger_type
    if body.trigger_config is not None:
        wf.trigger_config = body.trigger_config

    wf.version += 1
    await db.commit()
    await db.refresh(wf)
    return WorkflowResponse.model_validate(wf)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: UUID,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.org_id == current_user.org_id,
        )
    )
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    await db.delete(wf)
    await db.commit()


@router.post("/{workflow_id}/execute", response_model=ExecutionResponse, status_code=status.HTTP_202_ACCEPTED)
async def execute_workflow(
    workflow_id: UUID,
    body: WorkflowExecuteRequest,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> ExecutionResponse:
    """Trigger a workflow execution via Inngest background job."""
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.org_id == current_user.org_id,
        )
    )
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Create execution record
    execution = WorkflowExecution(
        workflow_id=wf.id,
        org_id=current_user.org_id,
        status="pending",
        trigger_type="manual",
        trigger_data=body.input or {},
        triggered_by=current_user.user_id,
    )
    db.add(execution)
    await db.flush()
    execution_id = str(execution.id)
    await db.commit()

    # Dispatch to Inngest
    from app.inngest.client import inngest_client

    await inngest_client.send(
        inngest.Event(
            name="nexusflow/workflow.run",
            data={
                "execution_id": execution_id,
                "workflow_id": str(workflow_id),
                "trigger_input": body.input or {},
            },
        )
    )

    return ExecutionResponse(
        execution_id=execution_id,
        workflow_id=str(workflow_id),
        status="pending",
        stream_url=f"/stream/executions/{execution_id}",
    )


@router.get("/{workflow_id}/executions", response_model=list[ExecutionResponse])
async def list_executions(
    workflow_id: UUID,
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> list[ExecutionResponse]:
    result = await db.execute(
        select(WorkflowExecution)
        .where(
            WorkflowExecution.workflow_id == workflow_id,
            WorkflowExecution.org_id == current_user.org_id,
        )
        .order_by(WorkflowExecution.created_at.desc())
        .limit(50)
    )
    executions = result.scalars().all()
    return [
        ExecutionResponse(
            execution_id=str(e.id),
            workflow_id=str(e.workflow_id),
            status=e.status,
            stream_url=f"/stream/executions/{e.id}",
        )
        for e in executions
    ]


# Import inngest at function level to avoid circular imports
import inngest
