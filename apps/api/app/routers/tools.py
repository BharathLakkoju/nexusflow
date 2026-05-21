# Implements: F-030 (tools)
"""Tools CRUD + execution router."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.middleware.auth import UserInfo
from app.middleware.rbac import RequireMember, RequireViewer
from app.models.models import Tool
from app.schemas.schemas import ToolCreate, ToolExecuteRequest, ToolExecuteResponse, ToolResponse
from app.services.tool_service import execute_tool
from app.tools.registry import list_tools

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("/built-in", response_model=list[dict])
async def list_built_in_tools(
    current_user: UserInfo = Depends(RequireViewer),
) -> list[dict]:
    """List all built-in tools available to agents."""
    return list_tools()


@router.post("/execute", response_model=ToolExecuteResponse)
async def execute_tool_endpoint(
    body: ToolExecuteRequest,
    current_user: UserInfo = Depends(RequireMember),
) -> ToolExecuteResponse:
    """Execute a built-in tool directly."""
    body.org_id = str(current_user.org_id)
    return await execute_tool(tool_name=body.tool_name, request=body)


@router.post("", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_tool(
    body: ToolCreate,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> ToolResponse:
    """Register a custom HTTP-based tool."""
    tool = Tool(
        org_id=current_user.org_id,
        name=body.name,
        description=body.description,
        tool_type="http",
        config=body.config or {},
        schema=body.schema or {},
        created_by=current_user.user_id,
    )
    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    return ToolResponse.model_validate(tool)


@router.get("", response_model=list[ToolResponse])
async def list_custom_tools(
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> list[ToolResponse]:
    result = await db.execute(
        select(Tool).where(Tool.org_id == current_user.org_id)
    )
    tools = result.scalars().all()
    return [ToolResponse.model_validate(t) for t in tools]


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_tool(
    tool_id: UUID,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Tool).where(Tool.id == tool_id, Tool.org_id == current_user.org_id)
    )
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    await db.delete(tool)
    await db.commit()
