"""The single loop: decompose -> (per subtask) decide cost-vs-quality -> pay
on-chain -> work -> rate on-chain -> reputation update changes the next decision.
"""
from __future__ import annotations

import asyncio
import json

from . import config, llm_service
from .agent_service import apply_local_rating, candidates_for_skill, sync_reputation_from_chain
from .chain_service import chain
from .db import Decision, Payment, Rating, Run, Subtask, get_session
from .ws import bus

W_QUALITY = 1.0
W_COST = 0.3


def _utility(reputation: float, price_mon: float, max_price: float) -> float:
    norm_price = (price_mon / max_price) if max_price else 0.0
    return W_QUALITY * (reputation / 5.0) - W_COST * norm_price


def _scripted_score(idx: int) -> int:
    # Force the demo flip: the agent that wins subtask 0 gets a low score so a
    # different agent wins the next same-skill subtask.
    return 2 if idx == 0 else 5


async def run_task(run_id: int, prompt: str) -> None:
    try:
        await bus.emit(run_id, "run_started", {"prompt": prompt})

        subtasks = await asyncio.to_thread(llm_service.decompose_task, prompt)
        st_info: list[dict] = []
        with get_session() as s:
            for i, st in enumerate(subtasks):
                row = Subtask(run_id=run_id, idx=i, description=st["description"], skill=st["skill"])
                s.add(row)
                s.commit()
                s.refresh(row)
                st_info.append({"id": row.id, "idx": row.idx, "description": row.description, "skill": row.skill})
        await bus.emit(run_id, "decomposed", {"subtasks": [{"idx": r["idx"], "description": r["description"], "skill": r["skill"]} for r in st_info]})

        results: list[str] = []
        for st in st_info:
            await _run_subtask(run_id, st, context="\n".join(results), results=results)

        final = "\n\n".join(results)
        with get_session() as s:
            run = s.get(Run, run_id)
            run.status = "completed"
            run.final_result = final
            s.add(run)
            s.commit()
        await bus.emit(run_id, "run_completed", {"final_result": final})
    except Exception as e:
        with get_session() as s:
            run = s.get(Run, run_id)
            if run:
                run.status = "failed"
                s.add(run)
                s.commit()
        await bus.emit(run_id, "run_failed", {"error": str(e)})
        raise


async def _run_subtask(run_id: int, st: dict, context: str, results: list[str]) -> None:
    # 1. candidates + cost-vs-quality decision
    cands = candidates_for_skill(st["skill"])
    max_price = max((c.price_mon for c in cands), default=0.0)
    personas = {c.agent_id: c.persona for c in cands}
    candidates = []
    for c in cands:
        u = _utility(c.reputation, c.price_mon, max_price)
        candidates.append(
            {"agent_id": c.agent_id, "name": c.name, "price_mon": c.price_mon, "reputation": round(c.reputation, 2), "utility": round(u, 3)}
        )
    candidates.sort(key=lambda d: d["utility"], reverse=True)
    chosen = candidates[0]
    await bus.emit(run_id, "candidates_evaluated", {"subtask_idx": st["idx"], "skill": st["skill"], "candidates": candidates})

    reasoning = await asyncio.to_thread(llm_service.narrate_decision, st["description"], candidates, chosen)
    with get_session() as s:
        s.add(Decision(subtask_id=st["id"], candidates_json=json.dumps(candidates), selected_agent_id=chosen["agent_id"], utility=chosen["utility"], reasoning=reasoning))
        row2 = s.get(Subtask, st["id"])
        row2.status = "hiring"
        s.add(row2)
        s.commit()
    await bus.emit(run_id, "agent_selected", {"subtask_idx": st["idx"], "agent_id": chosen["agent_id"], "name": chosen["name"], "price_mon": chosen["price_mon"], "reputation": chosen["reputation"], "utility": chosen["utility"], "reasoning": reasoning})

    # 2. pay on-chain
    await _pay(run_id, st, chosen)

    # 3. work
    persona = personas.get(chosen["agent_id"], "")
    work = await asyncio.to_thread(llm_service.do_work, persona, st["skill"], st["description"], context)
    results.append(f"### {st['description']}\n{work}")
    with get_session() as s:
        row2 = s.get(Subtask, st["id"])
        row2.status = "working"
        s.add(row2)
        s.commit()
    await bus.emit(run_id, "work_received", {"subtask_idx": st["idx"], "agent_id": chosen["agent_id"], "name": chosen["name"], "output": work})

    # 4. rate on-chain -> reputation changes the NEXT decision
    await _rate(run_id, st, chosen, work)


async def _pay(run_id: int, st: dict, chosen: dict) -> dict:
    with get_session() as s:
        pay_row = Payment(subtask_id=st["id"], agent_id=chosen["agent_id"], amount_mon=chosen["price_mon"], status="sent")
        s.add(pay_row)
        s.commit()
        s.refresh(pay_row)
        pay_id = pay_row.id
    await bus.emit(run_id, "payment_sent", {"subtask_idx": st["idx"], "agent_id": chosen["agent_id"], "amount_mon": chosen["price_mon"]})

    result = {"tx_hash": "", "block": 0, "status": "skipped"}
    if chain.is_ready():
        try:
            result = await asyncio.to_thread(chain.pay_agent, chosen["agent_id"], st["id"], chosen["price_mon"])
        except Exception as e:
            result = {"tx_hash": "", "block": 0, "status": f"error:{e}"}
    with get_session() as s:
        p = s.get(Payment, pay_id)
        p.tx_hash = result.get("tx_hash", "")
        p.block = result.get("block", 0)
        p.status = result.get("status", "sent")
        s.add(p)
        sub = s.get(Subtask, st["id"])
        sub.status = "paid"
        s.add(sub)
        s.commit()
    await bus.emit(run_id, "payment_confirmed", {"subtask_idx": st["idx"], "agent_id": chosen["agent_id"], "amount_mon": chosen["price_mon"], "tx_hash": result.get("tx_hash", ""), "block": result.get("block", 0), "status": result.get("status", ""), "explorer": config.EXPLORER_TX_BASE + result.get("tx_hash", "") if result.get("tx_hash") else ""})
    return result


async def _rate(run_id: int, st: dict, chosen: dict, work: str) -> None:
    if config.SCRIPTED_RATINGS:
        score = _scripted_score(st["idx"])
    else:
        score = await asyncio.to_thread(llm_service.evaluate_quality, st["description"], work)

    rep_before = round(chosen["reputation"], 2)
    tx_hash = ""
    if chain.is_ready():
        try:
            res = await asyncio.to_thread(chain.rate_job, chosen["agent_id"], st["id"], score)
            tx_hash = res.get("tx_hash", "")
        except Exception as e:
            print(f"[rate] on-chain rate failed: {e}")
    apply_local_rating(chosen["agent_id"], score)

    with get_session() as s:
        s.add(Rating(subtask_id=st["id"], agent_id=chosen["agent_id"], score=score, tx_hash=tx_hash))
        sub = s.get(Subtask, st["id"])
        sub.status = "rated"
        s.add(sub)
        s.commit()

    # read the new reputation from the mirror
    from .db import Agent  # local import to avoid cycle at module load
    with get_session() as s:
        a = s.get(Agent, chosen["agent_id"])
        rep_after = round(a.reputation, 2) if a else rep_before

    await bus.emit(run_id, "reputation_updated", {"subtask_idx": st["idx"], "agent_id": chosen["agent_id"], "name": chosen["name"], "score": score, "reputation_before": rep_before, "reputation_after": rep_after, "tx_hash": tx_hash, "explorer": config.EXPLORER_TX_BASE + tx_hash if tx_hash else ""})
