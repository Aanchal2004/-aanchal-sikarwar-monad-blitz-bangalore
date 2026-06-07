"""Researcher Agent — gathers information and context."""

from __future__ import annotations

from typing import Any

from agents.base import call_llm, load_prompt, mock_output


async def run(plan_or_query: str, context: dict[str, Any] | None = None) -> tuple[str, dict]:
    """
    TODO: Connect to RAG pipeline for document retrieval.
    TODO: Add web search tool (Tavily, Serper, etc.)
    """
    system = load_prompt("researcher")
    try:
        output = await call_llm(system, plan_or_query, context)
        if "[MOCK RESPONSE]" in output:
            output = mock_output("researcher", plan_or_query) + "\n\nFindings: Monad supports EVM wallets and fast finality."
    except Exception:
        output = mock_output("researcher", plan_or_query)

    metadata = {"sources_found": 2, "agent": "researcher"}
    return output, metadata
