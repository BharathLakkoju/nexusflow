"""
Shared state type for the LangGraph multi-agent supervisor workflow.
"""
from __future__ import annotations

from typing import Any, Optional, TypedDict

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Shared state flowing through the multi-agent LangGraph."""

    # Core task
    task: str
    org_id: str
    execution_id: str
    model: str

    # Message history
    messages: list[BaseMessage]

    # Agent outputs
    plan: list[str]          # from planner
    research: str            # from research agent
    draft: str               # from executor
    critique: str            # from critic
    memory_context: str      # from memory agent
    rag_context: str         # from RAG node

    # Control flow
    next_agent: str          # supervisor decision
    revision_count: int
    max_revisions: int
    iteration_count: int
    max_iterations: int

    # Tool results
    tool_results: list[dict[str, Any]]

    # Output
    final_output: str
    reasoning_trace: list[str]

    # Config
    available_tools: list[str]
    agent_config: dict[str, Any]
