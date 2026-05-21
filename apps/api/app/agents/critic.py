"""
Critic agent: reviews executor output for quality and accuracy.
"""
from __future__ import annotations

import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.agents.state import AgentState
from app.config import settings

logger = logging.getLogger(__name__)

CRITIC_SYSTEM_PROMPT = """You are a quality-assurance critic AI. Your job is to rigorously 
evaluate outputs for quality, accuracy, completeness, and alignment with the task.

Evaluation criteria:
1. **Accuracy**: Is the information correct? Are claims supported?
2. **Completeness**: Does it fully address the task requirements?
3. **Clarity**: Is the output clear, well-organized, and readable?
4. **Quality**: Is the level of depth appropriate for the task?
5. **Alignment**: Does it follow the plan? Are all steps addressed?

Be constructive — identify specific issues and suggest improvements.

Respond with ONLY valid JSON:
{{
  "score": <1-10>,
  "approved": <true if score >= 7>,
  "issues": ["specific issue 1", ...],
  "suggestions": ["concrete suggestion 1", ...],
  "critique_summary": "brief overall assessment"
}}"""


def create_critic_agent(model: str) -> callable:
    """Factory: creates a critic agent node."""
    llm = ChatOpenAI(
        model=model,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.2,
        default_headers={"HTTP-Referer": settings.FRONTEND_URL, "X-Title": "NexusFlow AI"},
    )

    def critic_node(state: AgentState) -> AgentState:
        task = state["task"]
        draft = state.get("draft", "")
        plan = state.get("plan", [])
        revision_count = state.get("revision_count", 0)
        max_revisions = state.get("max_revisions", 2)

        if not draft:
            return {**state, "critique": "No draft to critique."}

        plan_str = "\n".join(f"{i+1}. {s}" for i, s in enumerate(plan)) if plan else "No explicit plan"

        messages = [
            SystemMessage(content=CRITIC_SYSTEM_PROMPT),
            HumanMessage(
                content=f"Task: {task}\n\nPlan:\n{plan_str}\n\n"
                        f"Draft to evaluate (revision {revision_count}):\n{draft}\n\n"
                        f"Evaluate this output thoroughly."
            ),
        ]

        try:
            response = llm.invoke(messages)
            content = response.content.strip()
            if "```" in content:
                content = content.split("```")[1].replace("json", "").strip()

            evaluation = json.loads(content)
            score = evaluation.get("score", 7)
            approved = evaluation.get("approved", score >= 7)
            issues = evaluation.get("issues", [])
            suggestions = evaluation.get("suggestions", [])
            summary = evaluation.get("critique_summary", "")

            # Build critique text for executor
            if issues or suggestions:
                critique_text = f"Quality Score: {score}/10\n"
                if issues:
                    critique_text += "Issues:\n" + "\n".join(f"- {i}" for i in issues) + "\n"
                if suggestions:
                    critique_text += "Suggestions:\n" + "\n".join(f"- {s}" for s in suggestions)
            else:
                critique_text = ""  # No critique needed

            logger.info(
                "[Critic] Score=%d approved=%s for execution=%s",
                score,
                approved,
                state.get("execution_id"),
            )

            new_trace = state.get("reasoning_trace", []) + [
                f"[Critic] Score: {score}/10, Approved: {approved}. {summary}"
            ]

            # If approved or max revisions reached, clear critique to signal completion
            if approved or revision_count >= max_revisions:
                critique_text = ""  # Signal supervisor to finish

            return {
                **state,
                "critique": critique_text,
                "reasoning_trace": new_trace,
            }
        except Exception as exc:
            logger.error("[Critic] Failed: %s", exc)
            return {**state, "critique": ""}  # Don't block on critic failure

    return critic_node
