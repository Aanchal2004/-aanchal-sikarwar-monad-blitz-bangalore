"""Dev-only: validate the orchestration loop + reputation flip WITHOUT the chain.
Seeds mirror reputations like register_agents.py will on-chain, runs the loop,
and prints the agent selected per subtask (expect a flip after the low rating).
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import config  # noqa: E402

# Default to mock for a deterministic flip check; pass "sarvam" to use real LLM.
config.LLM_PROVIDER = sys.argv[1] if len(sys.argv) > 1 else "mock"

from app.agent_service import load_agents  # noqa: E402
from app.chain_service import chain  # noqa: E402
from app.db import Agent, Run, get_session, init_db  # noqa: E402
from app import orchestrator  # noqa: E402
from app.ws import bus  # noqa: E402

# Offline logic/reasoning test: force chain off so we never send real txns.
chain.contract = None

SEED = {1: (9, 2), 2: (15, 3), 3: (13, 3)}  # agent_id -> (rep_sum, rep_jobs)


async def main() -> None:
    config.DB_PATH.unlink(missing_ok=True)
    init_db()
    load_agents()
    with get_session() as s:
        for aid, (rsum, rjobs) in SEED.items():
            a = s.get(Agent, aid)
            a.rep_sum, a.rep_jobs = rsum, rjobs
            s.add(a)
        run = Run(prompt="electric scooters in India")
        s.add(run)
        s.commit()
        s.refresh(run)
        run_id = run.id

    await orchestrator.run_task(run_id, "electric scooters in India")

    print("\n=== SELECTIONS PER SUBTASK ===")
    for ev in bus.history(run_id):
        if ev["type"] == "agent_selected":
            print(f"  subtask {ev['subtask_idx']}: {ev['name']} (rep {ev['reputation']}, {ev['price_mon']} MON, utility {ev['utility']})")
            print(f"      reasoning: {ev['reasoning']}")
        if ev["type"] == "reputation_updated":
            print(f"    -> {ev['name']} rated {ev['score']}: rep {ev['reputation_before']} -> {ev['reputation_after']}")
    print("\nFLIP CHECK: subtask 0 and subtask 1 are both 'research'; expect different agents.")


if __name__ == "__main__":
    asyncio.run(main())
