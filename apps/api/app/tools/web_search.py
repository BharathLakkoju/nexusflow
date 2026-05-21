# Implements: F-031 (web search tool)
"""
Web search tool: Tavily primary, DuckDuckGo fallback.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def run_web_search(input_data: dict[str, Any], org_id: str | None) -> dict:
    """
    Search the web using Tavily API with DuckDuckGo as fallback.
    
    Input: {"query": str, "max_results": int (optional, default 5)}
    Output: {"results": [...], "source": "tavily"|"duckduckgo"}
    """
    from app.config import settings

    query = input_data.get("query", "").strip()
    max_results = min(int(input_data.get("max_results", 5)), 10)

    if not query:
        raise ValueError("query is required for web_search")

    # Try Tavily first
    if settings.TAVILY_API_KEY:
        try:
            return await _tavily_search(query, max_results, settings.TAVILY_API_KEY)
        except Exception as e:
            logger.warning("Tavily search failed, falling back to DuckDuckGo: %s", e)

    # Fallback to DuckDuckGo
    return await _duckduckgo_search(query, max_results)


async def _tavily_search(query: str, max_results: int, api_key: str) -> dict:
    """Search using Tavily API."""
    from tavily import TavilyClient

    client = TavilyClient(api_key=api_key)
    # Run in thread since tavily SDK is sync
    import asyncio
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None,
        lambda: client.search(query=query, max_results=max_results, include_answer=True),
    )

    results = []
    for r in response.get("results", []):
        results.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", "")[:1000],
            "score": r.get("score", 0),
        })

    return {
        "results": results,
        "answer": response.get("answer", ""),
        "source": "tavily",
    }


async def _duckduckgo_search(query: str, max_results: int) -> dict:
    """Search using DuckDuckGo (no API key required)."""
    from duckduckgo_search import DDGS
    import asyncio

    loop = asyncio.get_event_loop()

    def _search():
        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=max_results))

    raw_results = await loop.run_in_executor(None, _search)

    results = []
    for r in raw_results:
        results.append({
            "title": r.get("title", ""),
            "url": r.get("href", ""),
            "content": r.get("body", "")[:1000],
            "score": 1.0,
        })

    return {"results": results, "answer": "", "source": "duckduckgo"}
