"""Executor Agent — produces final deliverable or takes action."""

from __future__ import annotations

from typing import Any

from agents.base import call_llm, load_prompt, mock_output


async def run(critic_output: str, context: dict[str, Any] | None = None) -> tuple[str, dict]:
    """
    TODO: Add tool calling (API calls, blockchain txs, file writes).
    TODO: Integrate wallet_agent for on-chain actions.
    """
    system = load_prompt("executor")
    try:
        output = await call_llm(system, critic_output, context)
        if "[MOCK RESPONSE]" in output:
            output = mock_output("executor", critic_output) + "\n\nFinal deliverable ready for demo."
    except Exception:
        output = mock_output("executor", critic_output)

    metadata = {"status": "completed", "agent": "executor"}
    return output, metadata
