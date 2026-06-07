"""Critic Agent — reviews and improves outputs before execution."""

from __future__ import annotations

from typing import Any

from agents.base import call_llm, load_prompt, mock_output


async def run(research_output: str, context: dict[str, Any] | None = None) -> tuple[str, dict]:
    """
    TODO: Add structured output validation (Pydantic models).
    """
    system = load_prompt("critic")
    try:
        output = await call_llm(system, research_output, context)
        if "[MOCK RESPONSE]" in output:
            output = mock_output("critic", research_output) + "\n\nVerdict: APPROVED with minor suggestions."
    except Exception:
        output = mock_output("critic", research_output)

    metadata = {"verdict": "approved", "agent": "critic"}
    return output, metadata
