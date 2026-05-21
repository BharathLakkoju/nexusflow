"""
LangChain tool wrappers for the multi-agent system.
Bridges the tool registry with LangChain's @tool interface.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

from langchain_core.tools import tool

from app.config import settings

logger = logging.getLogger(__name__)


@tool
def web_search(query: str) -> str:
    """Search the web for current information on a topic.
    
    Args:
        query: The search query to look up
    
    Returns:
        Search results as formatted text
    """
    from app.tools.web_search import run_web_search

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(run_web_search({"query": query}, None))
        loop.close()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Search failed: {e}"


@tool
def http_request(url: str, method: str = "GET", body: Optional[str] = None) -> str:
    """Make an HTTP request to a URL.
    
    Args:
        url: The URL to request
        method: HTTP method (GET, POST, PUT, DELETE)
        body: Optional JSON body for POST/PUT
    
    Returns:
        Response text
    """
    from app.tools.http_tool import run_http_request

    input_data = {"url": url, "method": method}
    if body:
        try:
            input_data["body"] = json.loads(body)
        except json.JSONDecodeError:
            input_data["body"] = body

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(run_http_request(input_data, None))
        loop.close()
        return str(result)[:5000]  # Truncate large responses
    except Exception as e:
        return f"HTTP request failed: {e}"


@tool
def execute_python(code: str) -> str:
    """Execute Python code in a sandboxed environment.
    
    Args:
        code: Python code to execute
    
    Returns:
        stdout output from the code execution
    """
    from app.tools.code_executor import run_code

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(run_code({"code": code, "language": "python"}, None))
        loop.close()
        return str(result.get("stdout", "")) or str(result.get("stderr", "No output"))
    except Exception as e:
        return f"Code execution failed: {e}"


# Map of tool name → LangChain tool object
LANGCHAIN_TOOLS: dict = {
    "web_search": web_search,
    "http_request": http_request,
    "execute_python": execute_python,
}


def get_tools_for_agent(tool_names: list[str]) -> list:
    """Return LangChain tool objects for the given tool names."""
    return [LANGCHAIN_TOOLS[name] for name in tool_names if name in LANGCHAIN_TOOLS]
