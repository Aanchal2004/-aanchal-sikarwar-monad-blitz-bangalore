"""Wallet Agent — handles blockchain wallet operations on Monad."""

from __future__ import annotations

from typing import Any

from agents.base import call_llm, load_prompt, mock_output


async def run(action: str, context: dict[str, Any] | None = None) -> tuple[str, dict]:
    """
    TODO: Integrate ethers.js / web3.py for real Monad testnet txs.
    TODO: See monad/wallet_examples.md and monad/transaction_examples.md.
    """
    system = load_prompt("wallet_agent")
    try:
        output = await call_llm(system, action, context)
        if "[MOCK RESPONSE]" in output:
            output = (
                mock_output("wallet", action)
                + "\n\nMock tx: 0xabc123... signed on Monad testnet (simulated)."
            )
    except Exception:
        output = mock_output("wallet", action)

    metadata = {
        "chain": "monad-testnet",
        "wallet_ready": False,
        "agent": "wallet",
    }
    return output, metadata
