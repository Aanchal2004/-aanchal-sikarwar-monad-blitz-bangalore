"""Planner Agent — decomposes user goals into actionable steps."""

from __future__ import annotations

from typing import Any

from agents.base import call_llm, load_prompt, mock_output


async def run(user_query: str, context: dict[str, Any] | None = None) -> tuple[str, dict]:
    """
    TODO: Integrate LangGraph node for planner.
    """
    system = load_prompt("planner")
    try:
        output = await call_llm(system, user_query, context)
        if "[MOCK RESPONSE]" in output:
            output = mock_output("planner", user_query) + "\n\nPlanned steps:\n1. Research\n2. Critique\n3. Execute"
    except Exception:
        output = mock_output("planner", user_query)

    metadata = {"steps_planned": 3, "agent": "planner"}
    return output, metadata
