"""Shared utilities."""

from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def load_prompt(name: str) -> str:
    """Load a prompt template from prompts/ directory."""
    path = PROMPTS_DIR / f"{name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"You are the {name} agent. Complete your task efficiently."
