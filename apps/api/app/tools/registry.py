# Implements: F-030 (agent tools)
"""
Tool registry: maps tool names to async handler functions.
"""
from __future__ import annotations

from typing import Any, Callable

from app.tools.code_executor import run_code
from app.tools.http_tool import run_http_request
from app.tools.web_search import run_web_search
from app.tools.file_tool import run_file_read

# Registry: tool_name → async handler(input_data: dict, org_id: str | None) → Any
TOOL_REGISTRY: dict[str, Callable] = {
    "web_search": run_web_search,
    "http_request": run_http_request,
    "execute_python": run_code,
    "file_read": run_file_read,
}


def list_tools() -> list[dict[str, str]]:
    """Return metadata for all registered tools."""
    descriptions = {
        "web_search": "Search the web for current information using Tavily or DuckDuckGo.",
        "http_request": "Make HTTP requests to external APIs (GET, POST, PUT, DELETE).",
        "execute_python": "Execute Python code in a sandboxed subprocess and return stdout.",
        "file_read": "Read a file from a Vercel Blob URL and return its content.",
    }
    return [
        {"name": name, "description": descriptions.get(name, "")}
        for name in TOOL_REGISTRY
    ]
