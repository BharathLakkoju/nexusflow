# Implements: F-015 (agent management), F-016 (agent execution)
"""
Agents router: CRUD + single agent run.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.middleware.auth import UserInfo
from app.middleware.rbac import RequireMember, RequireViewer
from app.models.models import Agent
from app.schemas.schemas import (
    AgentCreate,
    AgentResponse,
    AgentRunRequest,
    AgentRunResponse,
    AgentUpdate,
)
from app.services.agent_service import run_agent

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    body: AgentCreate,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> AgentResponse:
    agent = Agent(
        org_id=current_user.org_id,
        name=body.name,
        description=body.description,
        agent_type=body.agent_type,
        model=body.model or "openai/gpt-4o-mini",
        system_prompt=body.system_prompt,
        tools=body.tools or [],
        agent_types=body.agent_types or ["executor"],
        max_revisions=body.max_revisions or 2,
        max_iterations=body.max_iterations or 10,
        use_rag=body.use_rag or False,
        created_by=current_user.user_id,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return AgentResponse.model_validate(agent)


@router.get("", response_model=list[AgentResponse])
async def list_agents(
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> list[AgentResponse]:
    result = await db.execute(
        select(Agent).where(Agent.org_id == current_user.org_id)
        .order_by(Agent.created_at.desc())
    )
    agents = result.scalars().all()
    return [AgentResponse.model_validate(a) for a in agents]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: UUID,
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> AgentResponse:
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.org_id == current_user.org_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse.model_validate(agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: UUID,
    body: AgentUpdate,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> AgentResponse:
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.org_id == current_user.org_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    await db.commit()
    await db.refresh(agent)
    return AgentResponse.model_validate(agent)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: UUID,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id, Agent.org_id == current_user.org_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    await db.delete(agent)
    await db.commit()


@router.post("/{agent_id}/run", response_model=AgentRunResponse)
async def run_agent_endpoint(
    agent_id: UUID,
    body: AgentRunRequest,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> AgentRunResponse:
    """Run an agent and return the result synchronously (max 2min)."""
    return await run_agent(
        db=db,
        org_id=str(current_user.org_id),
        agent_id=str(agent_id),
        request=body,
    )
