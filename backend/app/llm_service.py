"""LLM service. Provider = Sarvam (default) or a deterministic mock fallback.

Note: sarvam-105b is a reasoning model -- it emits `reasoning_content` and only
fills `content` once it stops thinking, so we give generous token budgets and
fall back to reasoning_content / mock if `content` is empty.
"""
from __future__ import annotations

import json
import re
from typing import Optional

import httpx

from . import config

AVAILABLE_SKILLS = ["research", "writing"]


def _sarvam_chat(messages: list[dict], model: Optional[str] = None, max_tokens: int = 600, reasoning_effort=None) -> str:
    # reasoning_effort=None disables "thinking" so `content` is populated directly
    # and fast (these are reasoning models that otherwise burn tokens on
    # reasoning_content and leave content empty when truncated).
    headers = {"Authorization": f"Bearer {config.SARVAM_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": model or config.SARVAM_CHAT_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "reasoning_effort": reasoning_effort,
    }
    r = httpx.post(config.SARVAM_BASE_URL, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    msg = r.json()["choices"][0]["message"]
    return (msg.get("content") or msg.get("reasoning_content") or "").strip()


def _extract_json(text: str):
    m = re.search(r"\[.*\]|\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #
def decompose_task(prompt: str) -> list[dict]:
    """Return ordered subtasks: [{description, skill}]. skill in AVAILABLE_SKILLS."""
    if config.LLM_PROVIDER == "sarvam":
        try:
            sys_msg = (
                "You are a Manager Agent that breaks a task into 2-4 ordered subtasks for a "
                f"workforce of specialist agents. Allowed skills: {AVAILABLE_SKILLS}. "
                "Return ONLY a JSON array of objects with keys 'description' and 'skill'. "
                "Prefer multiple 'research' subtasks when the task needs gathering info."
            )
            out = _sarvam_chat(
                [{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}],
                max_tokens=900,
            )
            data = _extract_json(out)
            if isinstance(data, list) and data:
                cleaned = []
                for d in data:
                    skill = str(d.get("skill", "research")).lower()
                    if skill not in AVAILABLE_SKILLS:
                        skill = "research"
                    cleaned.append({"description": str(d.get("description", "")).strip(), "skill": skill})
                if cleaned:
                    return cleaned
        except Exception as e:
            print(f"[llm] decompose fell back to mock: {e}")
    return _mock_decompose(prompt)


def do_work(persona: str, skill: str, subtask: str, context: str = "") -> str:
    if config.LLM_PROVIDER == "sarvam":
        try:
            sys_msg = f"You are a specialist agent. Persona: {persona}. Skill: {skill}. Be concise and useful."
            user = f"Subtask: {subtask}"
            if context:
                user += f"\n\nContext so far:\n{context}"
            out = _sarvam_chat(
                [{"role": "system", "content": sys_msg}, {"role": "user", "content": user}],
                model=config.SARVAM_WORK_MODEL,
                max_tokens=500,
            )
            if out:
                return out
        except Exception as e:
            print(f"[llm] do_work fell back to mock: {e}")
    return f"[{skill}] {subtask[:80]} -> (mock output by an agent with persona '{persona[:40]}')."


def narrate_decision(subtask: str, candidates: list[dict], chosen: dict) -> str:
    """One or two sentences explaining WHY this agent was hired (cost vs quality)."""
    if config.LLM_PROVIDER == "sarvam":
        try:
            table = "; ".join(
                f"{c['name']} (rep {c['reputation']:.2f}, {c['price_mon']} MON, utility {c['utility']:.3f})"
                for c in candidates
            )
            sys_msg = (
                "You are a Manager Agent justifying a hiring decision in ONE short sentence. "
                "Explain the cost-vs-quality tradeoff. Be specific and businesslike."
            )
            user = f"Subtask: {subtask}\nCandidates: {table}\nSelected: {chosen['name']}."
            out = _sarvam_chat(
                [{"role": "system", "content": sys_msg}, {"role": "user", "content": user}],
                max_tokens=300,
            )
            if out:
                return out.split("\n")[0][:240]
        except Exception as e:
            print(f"[llm] narrate fell back to mock: {e}")
    return (
        f"Selected {chosen['name']} (rep {chosen['reputation']:.2f} @ {chosen['price_mon']} MON) "
        f"for the best utility score {chosen['utility']:.3f}."
    )


def evaluate_quality(subtask: str, work: str) -> int:
    """Return a score 1..5. Used only when SCRIPTED_RATINGS is off."""
    if config.LLM_PROVIDER == "sarvam":
        try:
            sys_msg = "Rate the deliverable 1-5 (integer only) for how well it satisfies the subtask. Reply with just the number."
            out = _sarvam_chat(
                [{"role": "system", "content": sys_msg}, {"role": "user", "content": f"Subtask: {subtask}\n\nDeliverable:\n{work}"}],
                max_tokens=200,
            )
            m = re.search(r"[1-5]", out)
            if m:
                return int(m.group(0))
        except Exception as e:
            print(f"[llm] evaluate fell back to mock: {e}")
    return 4


def _mock_decompose(prompt: str) -> list[dict]:
    return [
        {"description": f"Research the market size and trends for: {prompt}", "skill": "research"},
        {"description": f"Research the key competitors and risks for: {prompt}", "skill": "research"},
        {"description": f"Write a concise executive summary for: {prompt}", "skill": "writing"},
    ]
