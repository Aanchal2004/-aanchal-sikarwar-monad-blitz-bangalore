"""Memory Agent — stores and retrieves conversation / task context."""

from __future__ import annotations

from typing import Any

from agents.base import mock_output

# In-memory store for hackathon speed
_MEMORY: list[dict[str, Any]] = []


async def run(input_text: str, context: dict[str, Any] | None = None) -> tuple[str, dict]:
    """
    TODO: Replace with Redis, SQLite, or vector memory (LangMem).
    """
    entry = {"input": input_text, "context": context or {}}
    _MEMORY.append(entry)

    output = mock_output("memory", input_text) + f"\n\nStored {len(_MEMORY)} memory entries."
    metadata = {"memory_count": len(_MEMORY), "agent": "memory"}
    return output, metadata


def get_memory() -> list[dict[str, Any]]:
    return list(_MEMORY)
