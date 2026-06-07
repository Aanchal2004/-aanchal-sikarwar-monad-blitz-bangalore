"""Generate fresh EOAs for the Manager + specialist agents.

Writes wallets.json (gitignored). Testnet-only hot keys -- never use these
addresses on mainnet. The Manager wallet is the contract owner and the sole
transaction sender; specialists are receive-only.

Usage:
    python scripts/gen_wallets.py
"""
from __future__ import annotations

import json
from pathlib import Path

from eth_account import Account

BACKEND_DIR = Path(__file__).resolve().parent.parent
OUT = BACKEND_DIR / "wallets.json"

# agent_id 0 is reserved for the Manager; specialists start at 1.
SPECIALISTS = [
    {"agent_id": 1, "name": "Asha",   "skill": "research", "price_mon": 0.05, "persona": "Fast, concise market researcher. Bullet-point facts."},
    {"agent_id": 2, "name": "Bhavna", "skill": "research", "price_mon": 0.20, "persona": "Premium senior analyst. Thorough, nuanced, cites angles."},
    {"agent_id": 3, "name": "Chetan", "skill": "writing",  "price_mon": 0.10, "persona": "Crisp business copywriter. Clear, professional prose."},
]


def main() -> None:
    if OUT.exists():
        print(f"{OUT} already exists -- refusing to overwrite. Delete it to regenerate.")
        return

    manager = Account.create()
    data = {
        "manager": {"agent_id": 0, "address": manager.address, "private_key": manager.key.hex()},
        "specialists": [],
    }
    for s in SPECIALISTS:
        acct = Account.create()
        data["specialists"].append({**s, "address": acct.address, "private_key": acct.key.hex()})

    OUT.write_text(json.dumps(data, indent=2))
    print(f"Wrote {OUT}")
    print("\n=== FUND THIS MANAGER ADDRESS via https://faucet.monad.xyz ===")
    print(f"  MANAGER_ADDRESS = {manager.address}")
    print("Then copy MANAGER_ADDRESS + MANAGER_PRIVATE_KEY into backend/.env\n")
    print(f"  MANAGER_PRIVATE_KEY = {manager.key.hex()}")


if __name__ == "__main__":
    main()
