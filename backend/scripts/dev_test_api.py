"""Dev-only: exercise REST + WebSocket against a running server on :8000."""
from __future__ import annotations

import asyncio
import json

import httpx
import websockets

BASE = "http://127.0.0.1:8000"
WS = "ws://127.0.0.1:8000"


async def main() -> None:
    async with httpx.AsyncClient(timeout=30) as c:
        print("HEALTH:", (await c.get(f"{BASE}/health")).json())
        agents = (await c.get(f"{BASE}/agents")).json()
        print("AGENTS:", [(a["name"], a["skill"], a["price_mon"], a["reputation"]) for a in agents])
        run_id = (await c.post(f"{BASE}/tasks", json={"prompt": "Should we launch electric scooters in Bangalore?"})).json()["run_id"]
        print("RUN_ID:", run_id)

    async with websockets.connect(f"{WS}/ws/runs/{run_id}") as ws:
        while True:
            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=120))
            except asyncio.TimeoutError:
                print("timeout waiting for events")
                break
            t = msg["type"]
            if t == "agent_selected":
                print(f"  SELECTED st{msg['subtask_idx']}: {msg['name']} (util {msg['utility']}) -- {msg['reasoning'][:70]}")
            elif t == "payment_confirmed":
                print(f"  PAID st{msg['subtask_idx']}: {msg['amount_mon']} MON status={msg['status']} tx={msg['tx_hash'][:14]}")
            elif t == "reputation_updated":
                print(f"  RATED st{msg['subtask_idx']}: {msg['name']} {msg['score']} -> rep {msg['reputation_before']}->{msg['reputation_after']}")
            elif t == "run_completed":
                print("  RUN COMPLETED. final_result chars:", len(msg["final_result"]))
                break
            elif t == "run_failed":
                print("  RUN FAILED:", msg.get("error"))
                break

    async with httpx.AsyncClient(timeout=30) as c:
        snap = (await c.get(f"{BASE}/runs/{run_id}")).json()
        print("SNAPSHOT subtasks:", len(snap["subtasks"]), "payments:", len(snap["payments"]), "ratings:", len(snap["ratings"]))


if __name__ == "__main__":
    asyncio.run(main())
