# Implements: F-027 (memory management)
"""Memory CRUD and search router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.middleware.auth import UserInfo
from app.middleware.rbac import RequireMember, RequireViewer
from app.models.models import Memory
from app.schemas.schemas import MemoryCreate, MemoryResponse, MemorySearchRequest, MemorySearchResponse
from app.services.memory_service import search_memories, store_memory

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    body: MemoryCreate,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> MemoryResponse:
    mem = await store_memory(
        db=db,
        org_id=str(current_user.org_id),
        content=body.content,
        memory_type=body.memory_type,
        agent_id=str(body.agent_id) if body.agent_id else None,
        metadata=body.metadata or {},
    )
    return MemoryResponse.model_validate(mem)


@router.post("/search", response_model=MemorySearchResponse)
async def search_memory(
    body: MemorySearchRequest,
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
) -> MemorySearchResponse:
    results = await search_memories(
        db=db,
        org_id=str(current_user.org_id),
        query=body.query,
        top_k=body.top_k,
        memory_type=body.memory_type,
    )
    return MemorySearchResponse(results=results, total=len(results))


@router.get("", response_model=list[MemoryResponse])
async def list_memories(
    current_user: UserInfo = Depends(RequireViewer),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
) -> list[MemoryResponse]:
    result = await db.execute(
        select(Memory)
        .where(Memory.org_id == current_user.org_id)
        .order_by(Memory.created_at.desc())
        .limit(min(limit, 200))
    )
    mems = result.scalars().all()
    return [MemoryResponse.model_validate(m) for m in mems]


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: str,
    current_user: UserInfo = Depends(RequireMember),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Memory).where(Memory.id == memory_id, Memory.org_id == current_user.org_id)
    )
    mem = result.scalar_one_or_none()
    if not mem:
        raise HTTPException(status_code=404, detail="Memory not found")
    await db.delete(mem)
    await db.commit()
