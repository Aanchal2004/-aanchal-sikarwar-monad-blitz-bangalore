"""Monad chain service (web3.py). Single sender (Manager EOA) for all txns,
serialized with a lock so nonces never collide. Tries eth_sendRawTransactionSync
for instant receipts and falls back to send + poll.
"""
from __future__ import annotations

import json
import threading
from typing import Optional

from web3 import Web3

from . import config


class ChainService:
    def __init__(self) -> None:
        self.w3 = Web3(Web3.HTTPProvider(config.MONAD_RPC_URL))
        self._lock = threading.Lock()
        self.account = None
        self.contract = None
        self._sync_supported: Optional[bool] = None
        if config.MANAGER_PRIVATE_KEY:
            self.account = self.w3.eth.account.from_key(config.MANAGER_PRIVATE_KEY)
        if config.CONTRACT_ADDRESS and config.ABI_PATH.exists():
            abi = json.loads(config.ABI_PATH.read_text())
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(config.CONTRACT_ADDRESS), abi=abi
            )

    # --- reads ---
    def is_ready(self) -> bool:
        return self.account is not None and self.contract is not None and self.w3.is_connected()

    def balance_mon(self) -> float:
        return float(self.w3.from_wei(self.w3.eth.get_balance(self.account.address), "ether"))

    def get_reputation(self, agent_id: int) -> tuple[float, int]:
        avg_x100, jobs = self.contract.functions.reputation(agent_id).call()
        return (avg_x100 / 100.0, int(jobs))

    def get_agent(self, agent_id: int) -> dict:
        wallet, price, rating_sum, jobs, active = self.contract.functions.getAgent(agent_id).call()
        return {
            "wallet": wallet,
            "price_mon": float(self.w3.from_wei(price, "ether")),
            "rating_sum": int(rating_sum),
            "jobs": int(jobs),
            "active": active,
        }

    # --- writes (serialized) ---
    def _send(self, fn, value_wei: int = 0) -> dict:
        with self._lock:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx = fn.build_transaction(
                {
                    "from": self.account.address,
                    "nonce": nonce,
                    "chainId": config.MONAD_CHAIN_ID,
                    "gasPrice": self.w3.eth.gas_price,
                    "value": value_wei,
                }
            )
            try:
                tx["gas"] = int(self.w3.eth.estimate_gas(tx) * 1.3)
            except Exception:
                tx["gas"] = 300_000
            signed = self.account.sign_transaction(tx)
            raw = signed.raw_transaction
            tx_hash, receipt = self._send_raw(raw)
            return {
                "tx_hash": tx_hash,
                "block": int(receipt["blockNumber"]) if receipt else 0,
                "status": "confirmed" if (receipt and receipt.get("status") == 1) else "sent",
            }

    def _send_raw(self, raw):
        """Try eth_sendRawTransactionSync once; fall back to send + poll."""
        raw_hex = raw.hex() if hasattr(raw, "hex") else raw
        if not raw_hex.startswith("0x"):
            raw_hex = "0x" + raw_hex
        if self._sync_supported is not False:
            try:
                resp = self.w3.provider.make_request("eth_sendRawTransactionSync", [raw_hex])
                if "result" in resp and isinstance(resp["result"], dict):
                    self._sync_supported = True
                    rcpt = resp["result"]
                    return (rcpt.get("transactionHash", ""), {"blockNumber": int(rcpt.get("blockNumber", "0x0"), 16) if isinstance(rcpt.get("blockNumber"), str) else rcpt.get("blockNumber", 0), "status": int(rcpt.get("status", "0x1"), 16) if isinstance(rcpt.get("status"), str) else rcpt.get("status", 1)})
                if "error" in resp:
                    self._sync_supported = False
            except Exception:
                self._sync_supported = False
        # fallback
        h = self.w3.eth.send_raw_transaction(raw)
        receipt = self.w3.eth.wait_for_transaction_receipt(h, timeout=60)
        return (h.hex(), dict(receipt))

    def pay_agent(self, agent_id: int, job_id: int, price_mon: float) -> dict:
        value_wei = self.w3.to_wei(price_mon, "ether")
        return self._send(self.contract.functions.payAgent(agent_id, job_id), value_wei=value_wei)

    def rate_job(self, agent_id: int, job_id: int, score: int) -> dict:
        return self._send(self.contract.functions.rateJob(agent_id, job_id, score))

    def register_agent(self, agent_id: int, wallet: str, price_mon: float) -> dict:
        price_wei = self.w3.to_wei(price_mon, "ether")
        return self._send(self.contract.functions.registerAgent(agent_id, Web3.to_checksum_address(wallet), price_wei))


chain = ChainService()
