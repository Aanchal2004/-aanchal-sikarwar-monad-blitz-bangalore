"""
Multi-agent workflow orchestrator.

Flow: User Query → Planner → Researcher → Critic → Executor → Final Output

TODO: Convert to LangGraph StateGraph for production.
"""

from __future__ import annotations

import time
from typing import Any

from agents.critic_agent import run as critic_run
from agents.executor_agent import run as executor_run
from agents.planner_agent import run as planner_run
from agents.researcher_agent import run as researcher_run


async def run_workflow(user_query: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    ctx = context or {}
    steps: list[dict[str, Any]] = []

    # 1. Planner
    t0 = time.perf_counter()
    plan, plan_meta = await planner_run(user_query, ctx)
    steps.append({
        "agent": "planner",
        "output": plan,
        "duration_ms": int((time.perf_counter() - t0) * 1000),
        "metadata": plan_meta,
    })

    # 2. Researcher
    t0 = time.perf_counter()
    research, research_meta = await researcher_run(plan, {**ctx, "plan": plan})
    steps.append({
        "agent": "researcher",
        "output": research,
        "duration_ms": int((time.perf_counter() - t0) * 1000),
        "metadata": research_meta,
    })

    # 3. Critic
    t0 = time.perf_counter()
    critique, critic_meta = await critic_run(research, {**ctx, "research": research})
    steps.append({
        "agent": "critic",
        "output": critique,
        "duration_ms": int((time.perf_counter() - t0) * 1000),
        "metadata": critic_meta,
    })

    # 4. Executor
    t0 = time.perf_counter()
    final, exec_meta = await executor_run(critique, {**ctx, "critique": critique})
    steps.append({
        "agent": "executor",
        "output": final,
        "duration_ms": int((time.perf_counter() - t0) * 1000),
        "metadata": exec_meta,
    })

    return {
        "query": user_query,
        "steps": steps,
        "final_output": final,
    }


# LangGraph skeleton for hackathon extension
def build_langgraph_workflow():
    """
    TODO: Implement with LangGraph:

    from langgraph.graph import StateGraph

    class AgentState(TypedDict):
        query: str
        plan: str
        research: str
        critique: str
        final_output: str

    graph = StateGraph(AgentState)
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("critic", critic_node)
    graph.add_node("executor", executor_node)
    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "critic")
    graph.add_edge("critic", "executor")
    graph.add_edge("executor", END)
    return graph.compile()
    """
    raise NotImplementedError("TODO: Wire LangGraph — see docstring for skeleton")
