"""One command to get a pristine demo state: redeploy a fresh AgentMandi
(reputations start clean), auto-update .env, then register + seed agents.

Run this right before a rehearsal or the live demo, then restart the server
so it picks up the new contract address.

Usage:
    python scripts/reset_demo.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
PY = sys.executable


def run(script: str) -> None:
    print(f"\n=== {script} ===")
    r = subprocess.run([PY, str(BACKEND / "scripts" / script)], cwd=str(BACKEND))
    if r.returncode != 0:
        sys.exit(f"{script} failed (exit {r.returncode})")


def main() -> None:
    # Fresh local mirror too, so the server re-syncs from the new contract.
    (BACKEND / "agentmandi.db").unlink(missing_ok=True)
    run("deploy.py")          # deploys + writes new address into .env
    run("register_agents.py")  # registers + seeds baseline reputations
    print("\nPristine demo state ready. Restart the server to load the new contract.")


if __name__ == "__main__":
    main()
