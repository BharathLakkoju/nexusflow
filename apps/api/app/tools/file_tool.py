# Implements: F-034 (file tool)
"""
File read tool: downloads and returns text content from a Vercel Blob URL.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


async def run_file_read(input_data: dict[str, Any], org_id: str | None) -> dict:
    """
    Read a file from a Vercel Blob URL and return its text content.
    
    Input: {"url": str, "encoding": str (default "utf-8")}
    Output: {"content": str, "size_bytes": int, "url": str}
    """
    url = input_data.get("url", "").strip()
    encoding = input_data.get("encoding", "utf-8")

    if not url:
        raise ValueError("url is required for file_read")

    # Only allow vercel blob or known safe domains
    from urllib.parse import urlparse
    parsed = urlparse(url)
    allowed_hosts = {"vercel-storage.com", "blob.vercel-storage.com"}
    if not any(parsed.hostname and parsed.hostname.endswith(h) for h in allowed_hosts):
        raise ValueError(f"file_read only supports Vercel Blob URLs. Got: {parsed.hostname}")

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url)
        response.raise_for_status()

    content = response.content[:1_048_576]  # 1MB max
    text = content.decode(encoding, errors="replace")

    logger.info("[FileTool] Read %d bytes from %s", len(content), url)
    return {
        "content": text,
        "size_bytes": len(content),
        "url": url,
    }
