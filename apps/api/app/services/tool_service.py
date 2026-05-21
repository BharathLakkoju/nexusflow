"""
Tool service: registry and execution of all built-in tools.
Implements: F-030 (tool calling framework).
"""
import logging
import time
from typing import Any

from app.schemas.schemas import ToolExecuteRequest, ToolExecuteResponse

logger = logging.getLogger(__name__)


async def execute_tool(
    tool_name: str,
    request: ToolExecuteRequest,
) -> ToolExecuteResponse:
    """Route tool execution to the appropriate handler."""
    start_ms = int(time.time() * 1000)

    try:
        output = await _dispatch_tool(tool_name, request.input, request.org_id)
        latency = int(time.time() * 1000) - start_ms
        return ToolExecuteResponse(
            tool_name=tool_name,
            output=output,
            success=True,
            latency_ms=latency,
        )
    except Exception as exc:
        latency = int(time.time() * 1000) - start_ms
        logger.error("Tool '%s' failed: %s", tool_name, exc)
        return ToolExecuteResponse(
            tool_name=tool_name,
            output=None,
            success=False,
            error=str(exc)[:500],
            latency_ms=latency,
        )


async def _dispatch_tool(
    tool_name: str,
    input_data: dict[str, Any],
    org_id: str | None,
) -> Any:
    """Dispatch to correct tool handler."""
    from app.tools.registry import TOOL_REGISTRY

    handler = TOOL_REGISTRY.get(tool_name)
    if not handler:
        raise ValueError(f"Unknown tool: '{tool_name}'. Available: {list(TOOL_REGISTRY.keys())}")

    return await handler(input_data, org_id)
