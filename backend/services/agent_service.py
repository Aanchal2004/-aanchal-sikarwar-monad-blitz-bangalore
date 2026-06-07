"""Agent orchestration service — bridges API routes to agents/ package."""

from __future__ import annotations

import sys
import time
from pathlib import Path

from config import get_settings
from models.schemas import AgentRunResponse, WorkflowResponse, WorkflowStep
from services.llm_provider import get_llm_provider

# Add agents/ to path for hackathon simplicity
AGENTS_DIR = Path(__file__).resolve().parents[2] / "agents"
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR.parent))


async def run_single_agent(agent_type: str, input_text: str, context: dict) -> AgentRunResponse:
    settings = get_settings()
    has_key = bool(
        settings.openai_api_key
        or settings.anthropic_api_key
        or settings.openrouter_api_key
    )

    agent_map = {
        "planner": _run_planner,
        "researcher": _run_researcher,
        "executor": _run_executor,
        "critic": _run_critic,
        "wallet": _run_wallet,
        "memory": _run_memory,
    }

    runner = agent_map.get(agent_type)
    if not runner:
        return AgentRunResponse(
            agent_type=agent_type,
            output=f"Unknown agent type: {agent_type}. Available: {list(agent_map.keys())}",
            mock=True,
        )

    output, metadata = await runner(input_text, context)
    return AgentRunResponse(
        agent_type=agent_type,
        output=output,
        metadata=metadata,
        mock=not has_key,
    )


async def run_workflow(query: str, context: dict) -> WorkflowResponse:
    """Execute multi-agent workflow: Planner → Researcher → Critic → Executor."""
    from agents.workflow import run_workflow as _workflow  # noqa: WPS433

    start = time.perf_counter()
    result = await _workflow(query, context)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    settings = get_settings()
    has_key = bool(
        settings.openai_api_key
        or settings.anthropic_api_key
        or settings.openrouter_api_key
    )

    steps = [
        WorkflowStep(agent=s["agent"], output=s["output"], duration_ms=s.get("duration_ms", 0))
        for s in result.get("steps", [])
    ]
    if not steps:
        steps = [WorkflowStep(agent="workflow", output=result.get("final_output", ""), duration_ms=elapsed_ms)]

    return WorkflowResponse(
        query=query,
        steps=steps,
        final_output=result.get("final_output", ""),
        mock=not has_key,
    )


async def _run_planner(input_text: str, context: dict) -> tuple[str, dict]:
    from agents.planner_agent import run as planner_run

    return await planner_run(input_text, context)


async def _run_researcher(input_text: str, context: dict) -> tuple[str, dict]:
    from agents.researcher_agent import run as researcher_run

    return await researcher_run(input_text, context)


async def _run_executor(input_text: str, context: dict) -> tuple[str, dict]:
    from agents.executor_agent import run as executor_run

    return await executor_run(input_text, context)


async def _run_critic(input_text: str, context: dict) -> tuple[str, dict]:
    from agents.critic_agent import run as critic_run

    return await critic_run(input_text, context)


async def _run_wallet(input_text: str, context: dict) -> tuple[str, dict]:
    from agents.wallet_agent import run as wallet_run

    return await wallet_run(input_text, context)


async def _run_memory(input_text: str, context: dict) -> tuple[str, dict]:
    from agents.memory_agent import run as memory_run

    return await memory_run(input_text, context)


async def chat(messages: list[dict[str, str]], agent_id: str | None = None) -> tuple[str, bool]:
    settings = get_settings()
    provider = get_llm_provider()
    has_key = bool(
        settings.openai_api_key
        or settings.anthropic_api_key
        or settings.openrouter_api_key
    )
    reply = await provider.chat(messages)
    return reply, not has_key
