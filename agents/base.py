"""Base agent utilities for hackathon multi-agent framework."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Ensure backend is importable when running agents standalone
ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

PROMPTS_DIR = ROOT / "prompts"


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"You are the {name} agent."


async def call_llm(system_prompt: str, user_input: str, context: dict[str, Any] | None = None) -> str:
    """
    Call the configured LLM provider.

    TODO: Replace mock fallback with real LangChain/LangGraph integration.
    """
    from services.llm_provider import get_llm_provider

    context_str = ""
    if context:
        context_str = f"\n\nContext:\n{context}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{user_input}{context_str}"},
    ]
    provider = get_llm_provider()
    return await provider.chat(messages)


def mock_output(agent_name: str, input_text: str) -> str:
    return (
        f"[{agent_name.upper()} MOCK] Processed: {input_text[:300]}. "
        f"TODO: Wire real LLM via call_llm()."
    )
