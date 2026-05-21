"""
Memory service: store and retrieve agent memories using pgvector.
Supports short-term, long-term, episodic, and semantic memory types.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.vector import cosine_search
from app.models.models import Memory
from app.schemas.schemas import MemoryCreate, MemoryResponse, MemorySearchRequest
from app.services.embedding_service import embed_text, embed_texts

logger = logging.getLogger(__name__)


async def store_memory(
    db: AsyncSession,
    org_id: str,
    payload: MemoryCreate,
) -> Memory:
    """Store a memory entry with its embedding."""
    embedding = await embed_text(payload.content)

    expires_at = None
    if payload.expires_in_hours:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=payload.expires_in_hours)
    elif payload.memory_type == "short_term":
        # Short-term memories expire after 24 hours by default
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    memory = Memory(
        org_id=org_id,
        agent_id=payload.agent_id,
        execution_id=payload.execution_id,
        memory_type=payload.memory_type,
        content=payload.content,
        embedding=embedding,
        mem_metadata=payload.metadata or {},
        expires_at=expires_at,
    )
    db.add(memory)
    await db.commit()
    await db.refresh(memory)
    logger.info("Stored %s memory for org %s", payload.memory_type, org_id)
    return memory


async def search_memories(
    db: AsyncSession,
    org_id: str,
    request: MemorySearchRequest,
) -> list[dict]:
    """Semantic search over memories."""
    query_embedding = await embed_text(request.query)

    extra_filters = "expires_at IS NULL OR expires_at > NOW()"
    if request.memory_type:
        extra_filters += f" AND memory_type = '{request.memory_type}'"
    if request.agent_id:
        extra_filters += f" AND agent_id = '{request.agent_id}'"

    results = await cosine_search(
        session=db,
        table="memories",
        embedding_col="embedding",
        query_embedding=query_embedding,
        org_id=org_id,
        limit=request.top_k,
        extra_filters=extra_filters,
        select_cols="id, memory_type, content, mem_metadata, created_at",
    )
    return results


async def get_memories_for_context(
    db: AsyncSession,
    org_id: str,
    query: str,
    agent_id: Optional[str] = None,
    limit: int = 5,
) -> str:
    """Retrieve relevant memories and format as context string."""
    request = MemorySearchRequest(
        query=query,
        top_k=limit,
        agent_id=agent_id,
    )
    memories = await search_memories(db, org_id, request)
    if not memories:
        return ""

    lines = ["## Relevant Memory Context\n"]
    for m in memories:
        mem_type = m.get("memory_type", "unknown")
        content = m.get("content", "")
        score = m.get("similarity", 0.0)
        lines.append(f"[{mem_type.upper()} | relevance={score:.2f}] {content}")

    return "\n".join(lines)


async def summarize_and_compress_memories(
    db: AsyncSession,
    org_id: str,
    agent_id: Optional[str] = None,
) -> Optional[Memory]:
    """
    Compress old short-term memories into a single long-term summary.
    Called periodically to prevent context bloat.
    """
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
    from app.config import settings

    # Fetch old short-term memories (older than 6 hours)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=6)
    stmt = select(Memory).where(
        and_(
            Memory.org_id == org_id,
            Memory.memory_type == "short_term",
            Memory.created_at < cutoff,
        )
    )
    if agent_id:
        stmt = stmt.where(Memory.agent_id == agent_id)
    stmt = stmt.order_by(Memory.created_at)

    result = await db.execute(stmt)
    old_memories = result.scalars().all()

    if len(old_memories) < 3:
        return None

    # Summarize with LLM
    llm = ChatOpenAI(
        model=settings.DEFAULT_MODEL,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.3,
    )
    content_block = "\n".join(m.content for m in old_memories)
    summary_prompt = (
        f"Summarize the following short-term memories into a concise long-term memory:\n\n"
        f"{content_block}\n\nProvide a dense, factual summary in 3-5 sentences."
    )

    import asyncio
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None, lambda: llm.invoke([HumanMessage(content=summary_prompt)])
    )
    summary_text = response.content

    # Store as long-term memory
    summary_embedding = await embed_text(summary_text)
    summary_memory = Memory(
        org_id=org_id,
        agent_id=agent_id,
        memory_type="long_term",
        content=summary_text,
        embedding=summary_embedding,
        mem_metadata={"compressed_from": [str(m.id) for m in old_memories]},
    )
    db.add(summary_memory)

    # Delete the old short-term memories
    for m in old_memories:
        await db.delete(m)

    await db.commit()
    return summary_memory


async def purge_expired_memories(db: AsyncSession) -> int:
    """Remove expired memories. Called on a schedule."""
    result = await db.execute(
        delete(Memory).where(
            and_(
                Memory.expires_at.isnot(None),
                Memory.expires_at < datetime.now(timezone.utc),
            )
        )
    )
    await db.commit()
    count = result.rowcount
    logger.info("Purged %d expired memories", count)
    return count
