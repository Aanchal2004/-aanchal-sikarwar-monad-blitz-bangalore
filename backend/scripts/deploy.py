"""Compile AgentMandi.sol (solcx) and deploy to Monad testnet (web3.py).

Writes the ABI to app/contract_abi.json and prints the deployed address.
Requires backend/.env with a FUNDED MANAGER_PRIVATE_KEY.

Usage:
    python scripts/deploy.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# allow `import app.config`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import solcx  # noqa: E402
import solcx.install  # noqa: E402
from web3 import Web3  # noqa: E402

from app import config  # noqa: E402

# solcx 2.0.3 hardcodes the dead host solc-bin.ethereum.org; point it at the
# official mirror (same path layout) which resolves fine.
solcx.install.BINARY_DOWNLOAD_BASE = "https://binaries.soliditylang.org/{}-amd64/{}"

SOLC_VERSION = "0.8.24"
CONTRACT_PATH = config.BACKEND_DIR.parent / "contracts" / "AgentMandi.sol"


def compile_contract() -> tuple[list, str]:
    try:
        solcx.set_solc_version(SOLC_VERSION)
    except Exception:
        print(f"Installing solc {SOLC_VERSION} ...")
        solcx.install_solc(SOLC_VERSION)
        solcx.set_solc_version(SOLC_VERSION)

    source = CONTRACT_PATH.read_text()
    compiled = solcx.compile_standard(
        {
            "language": "Solidity",
            "sources": {"AgentMandi.sol": {"content": source}},
            "settings": {
                "outputSelection": {"*": {"*": ["abi", "evm.bytecode.object"]}},
                "optimizer": {"enabled": True, "runs": 200},
            },
        },
        solc_version=SOLC_VERSION,
    )
    c = compiled["contracts"]["AgentMandi.sol"]["AgentMandi"]
    abi = c["abi"]
    bytecode = c["evm"]["bytecode"]["object"]
    config.ABI_PATH.write_text(json.dumps(abi, indent=2))
    print(f"Compiled. ABI -> {config.ABI_PATH}")
    return abi, bytecode


def main() -> None:
    if not config.MANAGER_PRIVATE_KEY:
        sys.exit("MANAGER_PRIVATE_KEY missing in backend/.env")

    abi, bytecode = compile_contract()

    w3 = Web3(Web3.HTTPProvider(config.MONAD_RPC_URL))
    if not w3.is_connected():
        sys.exit(f"Cannot connect to RPC {config.MONAD_RPC_URL}")

    acct = w3.eth.account.from_key(config.MANAGER_PRIVATE_KEY)
    balance = w3.eth.get_balance(acct.address)
    print(f"Deployer: {acct.address}  balance: {w3.from_wei(balance, 'ether')} MON")
    if balance == 0:
        sys.exit("Deployer has 0 MON. Fund it via https://faucet.monad.xyz first.")

    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(acct.address)
    gas_price = w3.eth.gas_price
    tx = Contract.constructor().build_transaction(
        {
            "from": acct.address,
            "nonce": nonce,
            "chainId": config.MONAD_CHAIN_ID,
            "gasPrice": gas_price,
        }
    )
    try:
        tx["gas"] = int(w3.eth.estimate_gas(tx) * 1.3)
    except Exception:
        tx["gas"] = 1_500_000

    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print(f"Deploy tx: {config.EXPLORER_TX_BASE}{tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    addr = receipt.contractAddress
    print("\n=== DEPLOYED ===")
    print(f"AGENTMANDI_CONTRACT_ADDRESS = {addr}")
    print(f"Explorer: {config.EXPLORER_ADDR_BASE}{addr}")
    print("\nPaste that address into backend/.env then run scripts/register_agents.py")


if __name__ == "__main__":
    main()
