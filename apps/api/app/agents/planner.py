"""
Planner agent: decomposes complex tasks into step-by-step plans.
"""
from __future__ import annotations

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agents.state import AgentState
from app.config import settings

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """You are a strategic task planner AI. Your job is to decompose 
complex tasks into clear, actionable steps.

Guidelines:
- Break tasks into 3-7 concrete steps
- Each step should be specific and actionable
- Order steps logically (dependencies first)
- Consider what research or tools might be needed
- Keep steps concise (1-2 sentences each)

Respond with ONLY valid JSON:
{{"steps": ["step 1", "step 2", ...], "strategy": "brief overview of your approach"}}"""


def create_planner_agent(model: str) -> callable:
    """Factory: creates a planner agent node."""
    llm = ChatOpenAI(
        model=model,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.3,
        default_headers={"HTTP-Referer": settings.FRONTEND_URL, "X-Title": "NexusFlow AI"},
    )

    def planner_node(state: AgentState) -> AgentState:
        task = state["task"]
        research = state.get("research", "")
        memory_ctx = state.get("memory_context", "")

        context_parts = []
        if research:
            context_parts.append(f"Available research:\n{research[:1500]}")
        if memory_ctx:
            context_parts.append(f"Relevant memory:\n{memory_ctx[:500]}")
        context_block = "\n\n".join(context_parts)

        messages = [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=f"Task: {task}\n\n{context_block}"),
        ]

        try:
            response = llm.invoke(messages)
            content = response.content.strip()
            if "```" in content:
                content = content.split("```")[1].replace("json", "").strip()

            plan_data = json.loads(content)
            steps = plan_data.get("steps", [])
            strategy = plan_data.get("strategy", "")

            logger.info("[Planner] Created plan with %d steps for execution=%s", len(steps), state.get("execution_id"))

            new_trace = state.get("reasoning_trace", []) + [
                f"[Planner] Strategy: {strategy}",
                f"[Planner] Plan: " + " → ".join(steps),
            ]

            return {
                **state,
                "plan": steps,
                "reasoning_trace": new_trace,
            }
        except Exception as exc:
            logger.error("[Planner] Failed: %s", exc)
            # Fallback: single step
            return {**state, "plan": [task]}

    return planner_node
