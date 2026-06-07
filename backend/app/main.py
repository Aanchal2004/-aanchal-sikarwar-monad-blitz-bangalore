"""FastAPI app: REST + WebSocket for the AgentMandi operations console.
UI is built separately; this exposes everything it needs.
"""
from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import select

from . import config
from .agent_service import list_agents, load_agents, sync_reputation_from_chain
from .chain_service import chain
from .db import Agent, Decision, Payment, Rating, Run, Subtask, get_session, init_db
from . import orchestrator
from .ws import bus

app = FastAPI(title="AgentMandi", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskIn(BaseModel):
    prompt: str
    budget_mon: float = 0.6


class AgentIn(BaseModel):
    name: str
    skill: str
    price_mon: float
    persona: str = ""
    operator: str = "Independent"


@app.on_event("startup")
def _startup() -> None:
    config.ensure_deploy_files()
    init_db()
    load_agents()
    _preflight_check()


def _preflight_check() -> None:
    """Warn if on-chain reputation has drifted far from demo baseline.
    The flip only works reliably when MarketScope ~4.50 and CompEdge ~5.00.
    Run scripts/reset_demo.py + restart server to restore baseline."""
    if not chain.is_ready():
        return
    try:
        asha_rep, _  = chain.get_reputation(1)
        bhavna_rep, _ = chain.get_reputation(2)
        if asha_rep < 3.8 or bhavna_rep < 4.5:
            print("\n" + "="*60)
            print("[!] DEMO PREFLIGHT WARNING")
            print(f"   MarketScope reputation: {asha_rep:.2f}  (want >= 4.50)")
            print(f"   CompEdge reputation  : {bhavna_rep:.2f}  (want >= 5.00)")
            print("   Run: python scripts/reset_demo.py -> restart server")
            print("="*60 + "\n")
        else:
            print(f"[OK] Demo baseline OK -- MarketScope {asha_rep:.2f}, CompEdge {bhavna_rep:.2f}")
    except Exception as e:
        print(f"[preflight] could not check reputation: {e}")


def _agent_dto(a) -> dict:
    return {
        "agent_id": a.agent_id,
        "name": a.name,
        "skill": a.skill,
        "wallet": a.wallet,
        "price_mon": a.price_mon,
        "reputation": round(a.reputation, 2),
        "jobs": a.rep_jobs,
        "persona": a.persona,
        "operator": a.operator or "Independent",
        "explorer": config.EXPLORER_ADDR_BASE + a.wallet,
    }


@app.get("/health")
def health() -> dict:
    ready = chain.is_ready()
    return {
        "chain_ready": ready,
        "contract": config.CONTRACT_ADDRESS or None,
        "manager": config.MANAGER_ADDRESS or None,
        "balance_mon": (chain.balance_mon() if ready else None),
        "llm_provider": config.LLM_PROVIDER,
    }


@app.get("/agents")
def agents() -> list[dict]:
    sync_reputation_from_chain()
    return [_agent_dto(a) for a in list_agents()]


@app.post("/agents")
def register_new_agent(body: AgentIn) -> dict:
    if not chain.is_ready():
        raise HTTPException(status_code=503, detail="Chain not ready — check MANAGER_PRIVATE_KEY and CONTRACT_ADDRESS")

    # generate a fresh EOA for this specialist
    acct = chain.w3.eth.account.create()
    wallet = acct.address
    private_key = acct.key.hex()

    # next agent_id = current max + 1
    with get_session() as s:
        existing = list(s.exec(select(Agent)).all())
        agent_id = max((a.agent_id for a in existing), default=0) + 1

    # register on-chain (only owner / manager can call this)
    try:
        chain.register_agent(agent_id, wallet, body.price_mon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"On-chain registration failed: {e}")

    # persist in local DB
    with get_session() as s:
        a = Agent(
            agent_id=agent_id,
            name=body.name,
            skill=body.skill,
            wallet=wallet,
            price_mon=body.price_mon,
            persona=body.persona,
            operator=body.operator or "Independent",
        )
        s.add(a)
        s.commit()

    # persist wallet to wallets.json so it survives server restarts
    try:
        wallets = json.loads(config.WALLETS_PATH.read_text())
        wallets["specialists"].append({
            "agent_id": agent_id,
            "name": body.name,
            "skill": body.skill,
            "address": wallet,
            "private_key": private_key,
            "price_mon": body.price_mon,
            "persona": body.persona,
            "operator": body.operator or "Independent",
        })
        config.WALLETS_PATH.write_text(json.dumps(wallets, indent=2))
    except Exception as e:
        print(f"[register] wallets.json update failed (agent still live on-chain): {e}")

    with get_session() as s:
        a = s.get(Agent, agent_id)
        return _agent_dto(a)


@app.post("/tasks")
async def create_task(body: TaskIn) -> dict:
    with get_session() as s:
        run = Run(prompt=body.prompt, budget_mon=body.budget_mon)
        s.add(run)
        s.commit()
        s.refresh(run)
        run_id = run.id
    asyncio.create_task(orchestrator.run_task(run_id, body.prompt))
    return {"run_id": run_id}


@app.get("/runs/{run_id}")
def get_run(run_id: int) -> dict:
    with get_session() as s:
        run = s.get(Run, run_id)
        if not run:
            return {"error": "not found"}
        subtasks = list(s.exec(select(Subtask).where(Subtask.run_id == run_id).order_by(Subtask.idx)).all())
        st_ids = [st.id for st in subtasks]
        decisions = list(s.exec(select(Decision).where(Decision.subtask_id.in_(st_ids))).all()) if st_ids else []
        payments = list(s.exec(select(Payment).where(Payment.subtask_id.in_(st_ids))).all()) if st_ids else []
        ratings = list(s.exec(select(Rating).where(Rating.subtask_id.in_(st_ids))).all()) if st_ids else []
        confirmed = [p for p in payments if p.status == "confirmed"]
        spent = round(sum(p.amount_mon for p in confirmed), 6)
        budget = round(float(run.budget_mon or 0.0), 6)
        remaining = round(max(budget - spent, 0.0), 6)
        paid_count = len(payments)
        skipped = len([st for st in subtasks if st.status == "skipped"])

        # Cost savings vs always hiring the most expensive qualified agent.
        paid_subtask_ids = {p.subtask_id for p in payments}
        premium = 0.0
        for d in decisions:
            if d.subtask_id in paid_subtask_ids:
                try:
                    cands = __import__("json").loads(d.candidates_json)
                    if cands:
                        premium += max(c["price_mon"] for c in cands)
                except Exception:
                    pass
        premium = round(premium, 6)
        cost_saved = round(max(premium - spent, 0.0), 6)
        cost_saved_pct = round((cost_saved / premium * 100), 1) if premium > 0 else 0.0

        # Confirmation latency + settlement count (the Monad story).
        latencies = [p.latency_ms for p in payments if getattr(p, "latency_ms", 0)]
        avg_conf_ms = round(sum(latencies) / len(latencies)) if latencies else 0
        settlements = len(payments) + len(ratings)

        hiring_changes_rep = sum(
            1 for d in decisions
            if d.selected_agent_id and d.reasoning
            and ("Previously hired" in d.reasoning or "reputation fell" in d.reasoning or "switching to" in d.reasoning)
        )

        summary = {
            "total_spent_mon": spent,
            "payments": paid_count,
            "confirmed": len(confirmed),
            "agents_hired": len({p.agent_id for p in payments}),
            "budget_mon": budget,
            "spent_mon": spent,
            "remaining_mon": remaining,
            "budget_utilization_pct": round((spent / budget * 100), 1) if budget > 0 else 0.0,
            "avg_cost_per_subtask": round((spent / paid_count), 6) if paid_count else 0.0,
            "subtasks_skipped": skipped,
            "premium_cost_mon": premium,
            "cost_saved_mon": cost_saved,
            "cost_saved_pct": cost_saved_pct,
            "avg_confirmation_ms": avg_conf_ms,
            "settlements": settlements,
            "hiring_changes_rep": hiring_changes_rep,
        }
        return {
            "run": {"id": run.id, "prompt": run.prompt, "budget_mon": run.budget_mon, "status": run.status, "final_result": run.final_result, "created_at": run.created_at},
            "summary": summary,
            "subtasks": [{"id": st.id, "idx": st.idx, "description": st.description, "skill": st.skill, "status": st.status} for st in subtasks],
            "decisions": [{"subtask_id": d.subtask_id, "selected_agent_id": d.selected_agent_id, "utility": d.utility, "reasoning": d.reasoning, "candidates": __import__("json").loads(d.candidates_json)} for d in decisions],
            "payments": [{"subtask_id": p.subtask_id, "agent_id": p.agent_id, "amount_mon": p.amount_mon, "tx_hash": p.tx_hash, "block": p.block, "status": p.status, "latency_ms": p.latency_ms, "explorer": (config.EXPLORER_TX_BASE + p.tx_hash) if p.tx_hash else ""} for p in payments],
            "ratings": [{"subtask_id": r.subtask_id, "agent_id": r.agent_id, "score": r.score, "tx_hash": r.tx_hash} for r in ratings],
            "events": bus.history(run_id),
        }


@app.websocket("/ws/runs/{run_id}")
async def ws_run(websocket: WebSocket, run_id: int) -> None:
    await websocket.accept()
    await bus.subscribe(run_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await bus.unsubscribe(run_id, websocket)
    except Exception:
        await bus.unsubscribe(run_id, websocket)
