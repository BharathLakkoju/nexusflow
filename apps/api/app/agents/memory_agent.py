"""
Memory agent: retrieves and injects relevant context from past interactions.
"""
from __future__ import annotations

import logging

from app.agents.state import AgentState

logger = logging.getLogger(__name__)


def create_memory_agent() -> callable:
    """Factory: creates a memory agent node. Uses memory_service (no LLM needed for retrieval)."""

    async def memory_node_async(state: AgentState, db) -> AgentState:
        from app.services.memory_service import get_memories_for_context

        org_id = state.get("org_id", "")
        task = state["task"]

        try:
            memory_context = await get_memories_for_context(
                db=db,
                org_id=org_id,
                query=task,
                top_k=5,
            )
            logger.info("[Memory] Retrieved context for execution=%s", state.get("execution_id"))
            new_trace = state.get("reasoning_trace", []) + [
                f"[Memory] Retrieved {len(memory_context)} chars of context"
            ]
            return {**state, "memory_context": memory_context, "reasoning_trace": new_trace}
        except Exception as exc:
            logger.error("[Memory] Failed: %s", exc)
            return {**state, "memory_context": ""}

    def memory_node_sync(state: AgentState) -> AgentState:
        """Synchronous wrapper — memory is pre-loaded by workflow engine before graph execution."""
        return state

    return memory_node_sync
