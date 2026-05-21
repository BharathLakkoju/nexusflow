"""
Research agent: gathers information using web search and RAG.
"""
from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agents.state import AgentState
from app.agents.tools import get_tools_for_agent
from app.config import settings

logger = logging.getLogger(__name__)

RESEARCH_SYSTEM_PROMPT = """You are a research specialist AI. Your job is to gather accurate, 
current information to help answer the given task.

Use the web_search tool to find relevant information. Search multiple angles:
1. Direct information about the topic
2. Related context and background  
3. Recent developments or data

Synthesize your findings into a clear, structured research report that will help 
the other agents complete the task. Be specific and cite what you found."""


def create_research_agent(model: str) -> callable:
    """Factory: creates a research agent node."""
    tools = get_tools_for_agent(["web_search", "http_request"])
    llm = ChatOpenAI(
        model=model,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.1,
        default_headers={"HTTP-Referer": settings.FRONTEND_URL, "X-Title": "NexusFlow AI"},
    ).bind_tools(tools)

    def research_node(state: AgentState) -> AgentState:
        task = state["task"]
        plan = state.get("plan", [])
        rag_context = state.get("rag_context", "")

        context_block = ""
        if rag_context:
            context_block = f"\n\nAvailable document context:\n{rag_context[:2000]}"
        if plan:
            context_block += f"\n\nCurrent plan:\n" + "\n".join(f"- {s}" for s in plan)

        messages = [
            SystemMessage(content=RESEARCH_SYSTEM_PROMPT),
            HumanMessage(content=f"Research task: {task}{context_block}"),
        ]

        try:
            # Agentic loop: allow tool calls
            response = llm.invoke(messages)
            research_text = response.content

            # If the model made tool calls, process them
            if hasattr(response, "tool_calls") and response.tool_calls:
                from langchain_core.messages import ToolMessage
                tool_results = []
                for tc in response.tool_calls:
                    tool_fn = next(
                        (t for t in tools if t.name == tc["name"]), None
                    )
                    if tool_fn:
                        result = tool_fn.invoke(tc["args"])
                        tool_results.append({"tool": tc["name"], "result": str(result)[:1000]})

                # Summarize tool results
                tool_summary = "\n".join(
                    f"[{r['tool']}]: {r['result']}" for r in tool_results
                )
                # Second pass: synthesize findings
                synthesis_messages = messages + [
                    response,
                    HumanMessage(
                        content=f"Tool results:\n{tool_summary}\n\nNow synthesize a research report."
                    ),
                ]
                second_response = ChatOpenAI(
                    model=model,
                    openai_api_key=settings.OPENROUTER_API_KEY,
                    openai_api_base="https://openrouter.ai/api/v1",
                    temperature=0.1,
                    default_headers={"HTTP-Referer": settings.FRONTEND_URL, "X-Title": "NexusFlow AI"},
                ).invoke(synthesis_messages)
                research_text = second_response.content

            logger.info("[Research] Completed research for execution=%s", state.get("execution_id"))

            new_trace = state.get("reasoning_trace", []) + [
                f"[Research] Gathered information: {len(research_text)} chars"
            ]

            return {
                **state,
                "research": research_text,
                "reasoning_trace": new_trace,
            }
        except Exception as exc:
            logger.error("[Research] Failed: %s", exc)
            return {**state, "research": f"Research failed: {exc}"}

    return research_node
