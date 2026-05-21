"""
Embedding service: generates vector embeddings via OpenRouter.
Uses LangChain's OpenAIEmbeddings with OpenRouter base URL.
"""
import logging
from functools import lru_cache

from langchain_openai import OpenAIEmbeddings

from app.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_embedding_model() -> OpenAIEmbeddings:
    """Returns a cached OpenAIEmbeddings instance pointed at OpenRouter."""
    return OpenAIEmbeddings(
        model=settings.DEFAULT_EMBEDDING_MODEL,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        dimensions=1536,
    )


async def embed_text(text: str) -> list[float]:
    """Embed a single string, returns 1536-dim vector."""
    model = get_embedding_model()
    # LangChain embeddings are sync; run in thread pool for async context
    import asyncio
    loop = asyncio.get_event_loop()
    embedding = await loop.run_in_executor(None, model.embed_query, text)
    return embedding


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Batch embed multiple strings."""
    if not texts:
        return []
    model = get_embedding_model()
    import asyncio
    loop = asyncio.get_event_loop()
    embeddings = await loop.run_in_executor(None, model.embed_documents, texts)
    return embeddings
