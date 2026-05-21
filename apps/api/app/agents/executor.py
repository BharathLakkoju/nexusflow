"""
Executor agent: performs the actual task — writes, codes, generates, transforms.
"""
from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agents.state import AgentState
from app.agents.tools import get_tools_for_agent
from app.config import settings

logger = logging.getLogger(__name__)

EXECUTOR_SYSTEM_PROMPT = """You are an expert task executor AI. You produce high-quality outputs 
by following plans, using research, and applying your skills.

When executing:
- Follow the plan steps in order
- Use research context when available
- Use tools when needed (code execution, HTTP requests)
- Address any critique from previous revisions
- Be thorough, accurate, and well-structured
- Format output clearly (use markdown when appropriate)"""


def create_executor_agent(model: str) -> callable:
    """Factory: creates an executor agent node."""
    tools = get_tools_for_agent(["execute_python", "http_request", "web_search"])
    llm = ChatOpenAI(
        model=model,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.5,
        default_headers={"HTTP-Referer": settings.FRONTEND_URL, "X-Title": "NexusFlow AI"},
    ).bind_tools(tools)

    base_llm = ChatOpenAI(
        model=model,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.5,
        default_headers={"HTTP-Referer": settings.FRONTEND_URL, "X-Title": "NexusFlow AI"},
    )

    def executor_node(state: AgentState) -> AgentState:
        task = state["task"]
        plan = state.get("plan", [])
        research = state.get("research", "")
        rag_context = state.get("rag_context", "")
        critique = state.get("critique", "")
        prev_draft = state.get("draft", "")
        memory_ctx = state.get("memory_context", "")

        context_parts = [f"Task: {task}"]
        if plan:
            context_parts.append("Plan:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(plan)))
        if research:
            context_parts.append(f"Research findings:\n{research[:2000]}")
        if rag_context:
            context_parts.append(f"Document context:\n{rag_context[:1500]}")
        if memory_ctx:
            context_parts.append(f"Relevant memory:\n{memory_ctx[:500]}")
        if critique and prev_draft:
            context_parts.append(
                f"Previous draft (revision {state.get('revision_count', 0)}):\n{prev_draft[:1000]}"
                f"\n\nCritique to address:\n{critique}"
            )

        user_prompt = "\n\n".join(context_parts) + "\n\nNow execute the task and produce the output."

        messages = [
            SystemMessage(content=EXECUTOR_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = llm.invoke(messages)
            draft = response.content

            # Process any tool calls
            if hasattr(response, "tool_calls") and response.tool_calls:
                tool_result_texts = []
                all_tools = get_tools_for_agent(["execute_python", "http_request", "web_search"])
                tool_map = {t.name: t for t in all_tools}

                for tc in response.tool_calls:
                    tool_fn = tool_map.get(tc["name"])
                    if tool_fn:
                        result = tool_fn.invoke(tc["args"])
                        tool_result_texts.append(f"[{tc['name']}]:\n{str(result)[:2000]}")

                # Incorporate tool results into final draft
                tool_block = "\n\n".join(tool_result_texts)
                finalize_messages = messages + [
                    response,
                    HumanMessage(
                        content=f"Tool outputs:\n{tool_block}\n\nNow write the final complete output."
                    ),
                ]
                final_response = base_llm.invoke(finalize_messages)
                draft = final_response.content

            rev_count = state.get("revision_count", 0)
            if critique:
                rev_count += 1

            logger.info("[Executor] Produced draft (%d chars) for execution=%s", len(draft), state.get("execution_id"))

            new_trace = state.get("reasoning_trace", []) + [
                f"[Executor] Produced output: {len(draft)} chars (revision {rev_count})"
            ]

            return {
                **state,
                "draft": draft,
                "revision_count": rev_count,
                "reasoning_trace": new_trace,
                "critique": "",  # Clear critique after addressing
            }
        except Exception as exc:
            logger.error("[Executor] Failed: %s", exc)
            return {**state, "draft": f"Execution failed: {exc}"}

    return executor_node
