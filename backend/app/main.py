"""FastAPI app: REST + WebSocket for the AgentMandi operations console.
UI is built separately; this exposes everything it needs.
"""
from __future__ import annotations

import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import select

from . import config
from .agent_service import list_agents, load_agents, sync_reputation_from_chain
from .chain_service import chain
from .db import Decision, Payment, Rating, Run, Subtask, get_session, init_db
from . import orchestrator
from .ws import bus

app = FastAPI(title="AgentMandi", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskIn(BaseModel):
    prompt: str


@app.on_event("startup")
def _startup() -> None:
    init_db()
    load_agents()


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


@app.post("/tasks")
async def create_task(body: TaskIn) -> dict:
    with get_session() as s:
        run = Run(prompt=body.prompt)
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
        return {
            "run": {"id": run.id, "prompt": run.prompt, "status": run.status, "final_result": run.final_result, "created_at": run.created_at},
            "subtasks": [{"id": st.id, "idx": st.idx, "description": st.description, "skill": st.skill, "status": st.status} for st in subtasks],
            "decisions": [{"subtask_id": d.subtask_id, "selected_agent_id": d.selected_agent_id, "utility": d.utility, "reasoning": d.reasoning, "candidates": __import__("json").loads(d.candidates_json)} for d in decisions],
            "payments": [{"subtask_id": p.subtask_id, "agent_id": p.agent_id, "amount_mon": p.amount_mon, "tx_hash": p.tx_hash, "block": p.block, "status": p.status, "explorer": (config.EXPLORER_TX_BASE + p.tx_hash) if p.tx_hash else ""} for p in payments],
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
