"""Register specialist agents on the deployed AgentMandi contract and seed
starting reputations (so cost-vs-quality tradeoffs are real on day one).

Requires backend/.env with AGENTMANDI_CONTRACT_ADDRESS + funded MANAGER_PRIVATE_KEY,
and wallets.json from gen_wallets.py.

Usage:
    python scripts/register_agents.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from web3 import Web3  # noqa: E402

from app import config  # noqa: E402

# Seed ratings (score, count) per agent_id -> builds a believable starting history.
# Bhavna (premium) starts highest, Asha (cheap) solid, Chetan (writer) good.
SEED_RATINGS = {
    1: [(5, 1), (4, 1)],          # Asha  -> avg 4.50
    2: [(5, 3)],                  # Bhavna -> avg 5.00
    3: [(5, 1), (4, 1), (4, 1)],  # Chetan -> avg 4.33
}


def main() -> None:
    if not config.CONTRACT_ADDRESS:
        sys.exit("AGENTMANDI_CONTRACT_ADDRESS missing in backend/.env (deploy first)")
    if not config.ABI_PATH.exists():
        sys.exit("contract_abi.json missing -- run scripts/deploy.py first")

    wallets = json.loads(config.WALLETS_PATH.read_text())
    abi = json.loads(config.ABI_PATH.read_text())

    w3 = Web3(Web3.HTTPProvider(config.MONAD_RPC_URL))
    acct = w3.eth.account.from_key(config.MANAGER_PRIVATE_KEY)
    contract = w3.eth.contract(address=Web3.to_checksum_address(config.CONTRACT_ADDRESS), abi=abi)

    def send(fn):
        nonce = w3.eth.get_transaction_count(acct.address)
        tx = fn.build_transaction(
            {
                "from": acct.address,
                "nonce": nonce,
                "chainId": config.MONAD_CHAIN_ID,
                "gasPrice": w3.eth.gas_price,
            }
        )
        try:
            tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.3)
        except Exception:
            tx["gas"] = 300_000
        signed = acct.sign_transaction(tx)
        h = w3.eth.send_raw_transaction(signed.raw_transaction)
        w3.eth.wait_for_transaction_receipt(h, timeout=120)
        return h.hex()

    for s in wallets["specialists"]:
        price_wei = w3.to_wei(s["price_mon"], "ether")
        h = send(contract.functions.registerAgent(s["agent_id"], Web3.to_checksum_address(s["address"]), price_wei))
        print(f"registered #{s['agent_id']} {s['name']} ({s['skill']}, {s['price_mon']} MON) tx={h}")
        for score, count in SEED_RATINGS.get(s["agent_id"], []):
            for _ in range(count):
                send(contract.functions.rateJob(s["agent_id"], 0, score))
        avg, jobs = contract.functions.reputation(s["agent_id"]).call()
        print(f"  -> on-chain reputation: {avg/100:.2f} over {jobs} jobs")

    print("\nAll agents registered + seeded.")


if __name__ == "__main__":
    main()
