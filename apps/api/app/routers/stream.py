# Implements: F-035 (SSE streaming)
"""
SSE streaming router: polls Upstash Redis list and streams events to client.
"""
import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.config import settings
from app.middleware.auth import UserInfo, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/stream", tags=["stream"])


async def _event_generator(execution_id: str, request: Request) -> AsyncGenerator[str, None]:
    """
    Poll Upstash Redis list every 500ms and yield new SSE events.
    Stops when client disconnects or execution_complete/execution_failed received.
    """
    from upstash_redis import Redis

    redis = Redis(
        url=settings.UPSTASH_REDIS_REST_URL,
        token=settings.UPSTASH_REDIS_REST_TOKEN,
    )
    key = f"execution:events:{execution_id}"
    cursor = 0
    terminal_types = {"execution_complete", "execution_failed", "execution_rejected"}

    # Send heartbeat immediately to establish connection
    yield "data: {\"type\": \"connected\"}\n\n"

    while True:
        # Check if client disconnected
        if await request.is_disconnected():
            break

        # Fetch new events from Redis list
        try:
            items = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: redis.lrange(key, cursor, -1),
            )
        except Exception as exc:
            logger.warning("[SSE] Redis fetch failed: %s", exc)
            items = []

        for item in items:
            cursor += 1
            try:
                event_data = json.loads(item) if isinstance(item, str) else item
                yield f"data: {json.dumps(event_data)}\n\n"

                # Stop streaming on terminal events
                if event_data.get("type") in terminal_types:
                    return
            except Exception:
                pass

        # Wait before next poll
        await asyncio.sleep(0.5)


@router.get("/executions/{execution_id}")
async def stream_execution(
    execution_id: str,
    request: Request,
    current_user: UserInfo = Depends(get_current_user),
) -> StreamingResponse:
    """Stream execution events via SSE."""
    return StreamingResponse(
        _event_generator(execution_id, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
