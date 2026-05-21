"""
Supervisor agent: routes tasks to the appropriate specialist agent.
Implements the ReAct-style supervisor pattern from LangGraph.
"""
from __future__ import annotations

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agents.state import AgentState
from app.config import settings

logger = logging.getLogger(__name__)

SUPERVISOR_SYSTEM_PROMPT = """You are a supervisor AI orchestrating a team of specialist agents to complete tasks.

Available agents:
- research: Gathers information from the web and knowledge bases
- planner: Breaks complex tasks into step-by-step plans
- executor: Executes tasks, writes code, generates content
- critic: Reviews outputs for quality, accuracy, and completeness
- memory: Retrieves relevant context from past interactions

Your job: Given the current task progress, decide WHICH agent should act next.

Rules:
1. Start with 'planner' for complex multi-step tasks, or 'executor' for simple direct tasks
2. Use 'research' when external information is needed
3. After executor produces a draft, use 'critic' to evaluate quality
4. After critique, return to 'executor' for revisions (max {max_revisions} revisions)
5. Use 'memory' when historical context would help
6. Output 'FINISH' when the task is complete and high quality

Current state:
- Task: {task}
- Plan ready: {has_plan}
- Research done: {has_research}
- Draft ready: {has_draft}
- Critique done: {has_critique}
- Revision count: {revision_count}/{max_revisions}
- Iteration: {iteration_count}/{max_iterations}

Respond with ONLY valid JSON:
{{"next": "agent_name_or_FINISH", "reason": "brief explanation"}}"""


def create_supervisor(model: str, max_revisions: int = 2) -> callable:
    """Factory: creates a supervisor node function."""
    llm = ChatOpenAI(
        model=model,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.2,
        default_headers={"HTTP-Referer": settings.FRONTEND_URL, "X-Title": "NexusFlow AI"},
    )

    def supervisor_node(state: AgentState) -> AgentState:
        prompt = SUPERVISOR_SYSTEM_PROMPT.format(
            task=state["task"][:500],
            has_plan=bool(state.get("plan")),
            has_research=bool(state.get("research")),
            has_draft=bool(state.get("draft")),
            has_critique=bool(state.get("critique")),
            revision_count=state.get("revision_count", 0),
            max_revisions=state.get("max_revisions", max_revisions),
            iteration_count=state.get("iteration_count", 0),
            max_iterations=state.get("max_iterations", 10),
        )

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content="Decide the next agent to act."),
        ]

        try:
            response = llm.invoke(messages)
            content = response.content.strip()
            # Extract JSON even if wrapped in markdown
            if "```" in content:
                content = content.split("```")[1].replace("json", "").strip()

            decision = json.loads(content)
            next_agent = decision.get("next", "executor")
            reason = decision.get("reason", "")

            logger.info(
                "[Supervisor] execution=%s → next=%s reason=%s",
                state.get("execution_id"),
                next_agent,
                reason,
            )

            new_trace = state.get("reasoning_trace", []) + [
                f"[Supervisor] iteration={state.get('iteration_count', 0)}: {reason}"
            ]

            return {
                **state,
                "next_agent": next_agent,
                "reasoning_trace": new_trace,
                "iteration_count": state.get("iteration_count", 0) + 1,
            }
        except Exception as exc:
            logger.error("[Supervisor] Decision failed: %s", exc)
            return {**state, "next_agent": "executor"}

    return supervisor_node


def supervisor_router(state: AgentState) -> str:
    """Conditional edge function: routes based on supervisor's decision."""
    next_agent = state.get("next_agent", "executor")
    iteration = state.get("iteration_count", 0)
    max_iter = state.get("max_iterations", 10)

    # Force finish if max iterations reached
    if iteration >= max_iter:
        logger.warning("[Supervisor] Max iterations reached, forcing FINISH")
        return "FINISH"

    return next_agent
