"""
pgvector helper functions for cosine similarity search.
Neon PostgreSQL has the vector extension available on all plans.
"""
from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def cosine_search(
    session: AsyncSession,
    table: str,
    embedding_col: str,
    query_embedding: list[float],
    org_id: str,
    limit: int = 10,
    extra_filters: str = "",
    select_cols: str = "*",
    min_score: float = 0.0,
) -> list[dict[str, Any]]:
    """
    Generic cosine similarity search using pgvector.
    Returns rows ordered by similarity (highest first).
    """
    vector_str = f"[{','.join(str(v) for v in query_embedding)}]"
    filter_clause = f"AND org_id = '{org_id}'" if org_id else ""
    if extra_filters:
        filter_clause += f" AND {extra_filters}"

    sql = text(f"""
        SELECT {select_cols},
               1 - ({embedding_col} <=> :embedding::vector) AS similarity
        FROM {table}
        WHERE {embedding_col} IS NOT NULL
          {filter_clause}
          AND 1 - ({embedding_col} <=> :embedding::vector) >= :min_score
        ORDER BY {embedding_col} <=> :embedding::vector
        LIMIT :limit
    """)

    result = await session.execute(
        sql,
        {
            "embedding": vector_str,
            "limit": limit,
            "min_score": min_score,
        },
    )
    rows = result.mappings().all()
    return [dict(row) for row in rows]


async def hybrid_search(
    session: AsyncSession,
    table: str,
    embedding_col: str,
    content_col: str,
    query_embedding: list[float],
    query_text: str,
    org_id: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Hybrid search: combine vector similarity + full-text search with RRF ranking.
    """
    vector_str = f"[{','.join(str(v) for v in query_embedding)}]"
    org_filter = f"AND org_id = '{org_id}'" if org_id else ""

    sql = text(f"""
        WITH vector_results AS (
            SELECT id,
                   ROW_NUMBER() OVER (ORDER BY {embedding_col} <=> :embedding::vector) AS rank
            FROM {table}
            WHERE {embedding_col} IS NOT NULL {org_filter}
            LIMIT 50
        ),
        text_results AS (
            SELECT id,
                   ROW_NUMBER() OVER (
                       ORDER BY ts_rank(
                           to_tsvector('english', {content_col}),
                           plainto_tsquery('english', :query)
                       ) DESC
                   ) AS rank
            FROM {table}
            WHERE to_tsvector('english', {content_col}) @@ plainto_tsquery('english', :query)
              {org_filter}
            LIMIT 50
        ),
        rrf_scores AS (
            SELECT
                COALESCE(v.id, t.id) AS id,
                COALESCE(1.0 / (60 + v.rank), 0) + COALESCE(1.0 / (60 + t.rank), 0) AS rrf_score
            FROM vector_results v
            FULL OUTER JOIN text_results t ON v.id = t.id
        )
        SELECT t.*, r.rrf_score
        FROM {table} t
        JOIN rrf_scores r ON t.id = r.id
        ORDER BY r.rrf_score DESC
        LIMIT :limit
    """)

    result = await session.execute(
        sql,
        {"embedding": vector_str, "query": query_text, "limit": limit},
    )
    rows = result.mappings().all()
    return [dict(row) for row in rows]
