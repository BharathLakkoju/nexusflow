"""
LangGraph multi-agent graph builder.
Wires supervisor + all specialist agents into a StateGraph.
"""
from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from app.agents.critic import create_critic_agent
from app.agents.executor import create_executor_agent
from app.agents.memory_agent import create_memory_agent
from app.agents.planner import create_planner_agent
from app.agents.research import create_research_agent
from app.agents.state import AgentState
from app.agents.supervisor import create_supervisor, supervisor_router

logger = logging.getLogger(__name__)


def build_agent_graph(
    model: str = "openai/gpt-4o-mini",
    max_revisions: int = 2,
    max_iterations: int = 10,
    available_agents: list[str] | None = None,
) -> StateGraph:
    """
    Build the complete LangGraph multi-agent StateGraph.
    
    Node routing:
      START → supervisor → [research|planner|executor|critic|memory|FINISH]
    """
    if available_agents is None:
        available_agents = ["research", "planner", "executor", "critic", "memory"]

    graph = StateGraph(AgentState)

    # Create nodes
    supervisor = create_supervisor(model=model, max_revisions=max_revisions)
    graph.add_node("supervisor", supervisor)

    if "research" in available_agents:
        research = create_research_agent(model=model)
        graph.add_node("research", research)

    if "planner" in available_agents:
        planner = create_planner_agent(model=model)
        graph.add_node("planner", planner)

    if "executor" in available_agents:
        executor = create_executor_agent(model=model)
        graph.add_node("executor", executor)

    if "critic" in available_agents:
        critic = create_critic_agent(model=model)
        graph.add_node("critic", critic)

    if "memory" in available_agents:
        memory = create_memory_agent()
        graph.add_node("memory", memory)

    # Entry point
    graph.set_entry_point("supervisor")

    # Supervisor routes to agents
    route_map = {agent: agent for agent in available_agents}
    route_map["FINISH"] = END

    graph.add_conditional_edges(
        "supervisor",
        supervisor_router,
        route_map,
    )

    # All agents return to supervisor after acting
    for agent in available_agents:
        graph.add_edge(agent, "supervisor")

    return graph.compile()


def get_initial_state(
    task: str,
    org_id: str,
    execution_id: str,
    model: str = "openai/gpt-4o-mini",
    max_revisions: int = 2,
    max_iterations: int = 10,
    available_tools: list[str] | None = None,
    memory_context: str = "",
    rag_context: str = "",
) -> AgentState:
    """Build the initial state dict for a new agent run."""
    return AgentState(
        task=task,
        org_id=org_id,
        execution_id=execution_id,
        model=model,
        messages=[],
        plan=[],
        research="",
        draft="",
        critique="",
        memory_context=memory_context,
        rag_context=rag_context,
        next_agent="supervisor",
        revision_count=0,
        max_revisions=max_revisions,
        iteration_count=0,
        max_iterations=max_iterations,
        tool_results=[],
        final_output="",
        reasoning_trace=[],
        available_tools=available_tools or ["web_search", "execute_python", "http_request"],
        agent_config={},
    )
