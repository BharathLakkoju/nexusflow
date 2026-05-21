"""
RAG (Retrieval-Augmented Generation) service.
Handles semantic search over document chunks using pgvector.
"""
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.vector import cosine_search, hybrid_search
from app.models.models import Document, DocumentChunk
from app.schemas.schemas import RAGSearchRequest, RAGSearchResponse, RAGSearchResult
from app.services.embedding_service import embed_text

logger = logging.getLogger(__name__)


async def search_documents(
    db: AsyncSession,
    org_id: str,
    request: RAGSearchRequest,
) -> RAGSearchResponse:
    """
    Semantic (or hybrid) search across all documents for an org.
    Returns relevant chunks with similarity scores.
    """
    query_embedding = await embed_text(request.query)

    # Build extra filter for specific document IDs
    extra_filters = "dc.document_id IN (SELECT id FROM documents WHERE org_id = '" + org_id + "' AND status = 'completed')"
    if request.document_ids:
        ids_str = ", ".join(f"'{str(did)}'" for did in request.document_ids)
        extra_filters += f" AND dc.document_id IN ({ids_str})"

    if request.use_hybrid:
        raw_results = await hybrid_search(
            session=db,
            table="document_chunks dc",
            embedding_col="dc.embedding",
            content_col="dc.content",
            query_embedding=query_embedding,
            query_text=request.query,
            org_id=org_id,
            limit=request.top_k,
        )
    else:
        raw_results = await cosine_search(
            session=db,
            table="document_chunks dc",
            embedding_col="dc.embedding",
            query_embedding=query_embedding,
            org_id=org_id,
            limit=request.top_k,
            extra_filters=extra_filters,
            select_cols="dc.id, dc.document_id, dc.content, dc.chunk_index, dc.chunk_metadata",
            min_score=request.min_score,
        )

    # Enrich with document names
    doc_ids = list({str(r["document_id"]) for r in raw_results})
    doc_map: dict[str, str] = {}
    if doc_ids:
        ids_str = ", ".join(f"'{did}'" for did in doc_ids)
        from sqlalchemy import text
        result = await db.execute(
            text(f"SELECT id::text, name FROM documents WHERE id::text IN ({ids_str})")
        )
        doc_map = {row[0]: row[1] for row in result}

    results = []
    for r in raw_results:
        doc_id = str(r.get("document_id", ""))
        results.append(
            RAGSearchResult(
                chunk_id=r["id"],
                document_id=r["document_id"],
                document_name=doc_map.get(doc_id, "Unknown"),
                content=r["content"],
                similarity=float(r.get("similarity", r.get("rrf_score", 0))),
                chunk_index=r.get("chunk_index", 0),
                metadata=r.get("chunk_metadata", {}),
            )
        )

    return RAGSearchResponse(
        query=request.query,
        results=results,
        total=len(results),
    )


async def build_rag_context(
    db: AsyncSession,
    org_id: str,
    query: str,
    top_k: int = 5,
    document_ids: Optional[list[UUID]] = None,
) -> str:
    """
    Retrieve relevant chunks and format as a context block for LLM prompts.
    Includes citation markers.
    """
    request = RAGSearchRequest(
        query=query,
        top_k=top_k,
        use_hybrid=True,
        document_ids=document_ids,
    )
    response = await search_documents(db, org_id, request)

    if not response.results:
        return ""

    context_parts = ["## Retrieved Context (Citations)\n"]
    for i, chunk in enumerate(response.results, 1):
        context_parts.append(
            f"[{i}] Source: '{chunk.document_name}' (chunk {chunk.chunk_index}, "
            f"relevance={chunk.similarity:.2f})\n{chunk.content}\n"
        )

    context_parts.append(
        "\nWhen using information from above, cite as [1], [2], etc."
    )
    return "\n".join(context_parts)
