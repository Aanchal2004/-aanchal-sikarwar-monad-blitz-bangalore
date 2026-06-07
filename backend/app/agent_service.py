"""Agent roster: loads specialist wallets/metadata into the SQLite mirror and
syncs reputation from chain. Specialists are in-process personas, but each owns
a real on-chain wallet, so payments to them are genuine on-chain transfers.
"""
from __future__ import annotations

import json

from sqlmodel import select

from . import config
from .chain_service import chain
from .db import Agent, get_session


def load_agents() -> list[Agent]:
    """Upsert specialists from wallets.json into the mirror; sync rep from chain."""
    wallets = json.loads(config.WALLETS_PATH.read_text())
    with get_session() as s:
        for spec in wallets["specialists"]:
            a = s.get(Agent, spec["agent_id"])
            if a is None:
                a = Agent(agent_id=spec["agent_id"])
            a.name = spec["name"]
            a.skill = spec["skill"]
            a.wallet = spec["address"]
            a.price_mon = spec["price_mon"]
            a.persona = spec.get("persona", "")
            a.operator = spec.get("operator", "") or "Independent"
            s.add(a)
        s.commit()
    sync_reputation_from_chain()
    return list_agents()


def sync_reputation_from_chain() -> None:
    if not chain.is_ready():
        return
    with get_session() as s:
        for a in s.exec(select(Agent)).all():
            try:
                avg, jobs = chain.get_reputation(a.agent_id)
                a.rep_jobs = jobs
                a.rep_sum = round(avg * jobs)
                s.add(a)
            except Exception as e:
                print(f"[agents] rep sync failed for #{a.agent_id}: {e}")
        s.commit()


def list_agents() -> list[Agent]:
    with get_session() as s:
        return list(s.exec(select(Agent).order_by(Agent.agent_id)).all())


def candidates_for_skill(skill: str) -> list[Agent]:
    with get_session() as s:
        rows = list(s.exec(select(Agent).where(Agent.skill == skill)).all())
    if not rows:  # fall back to any agent so a run never dead-ends
        rows = list_agents()
    return rows


def apply_local_rating(agent_id: int, score: int) -> None:
    """Optimistically update the mirror right after we submit rateJob on-chain."""
    with get_session() as s:
        a = s.get(Agent, agent_id)
        if a:
            a.rep_sum += score
            a.rep_jobs += 1
            s.add(a)
            s.commit()
