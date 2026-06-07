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

# Weights tuned so the flip fires reliably:
# from clean baseline (Asha 4.50/0.05 vs Bhavna 5.00/0.20):
#   before: Asha 0.825 wins, Bhavna 0.700
#   after rating=2 (Asha → 3.67): Asha 0.659, Bhavna 0.700 → Bhavna flips in ✓
# At W_COST=0.2 Bhavna never wins; at W_COST=0.4+ Asha wins even at 3.0 rep.
# W_COST=0.3 is the sweet spot — keep it, never change without re-checking math.
W_QUALITY = 1.0
W_COST = 0.3


def _utility(reputation: float, price_mon: float, max_price: float) -> float:
    norm_price = (price_mon / max_price) if max_price else 0.0
    return W_QUALITY * (reputation / 5.0) - W_COST * norm_price


def _scripted_score(idx: int) -> int:
    # Force the demo flip: the agent that wins subtask 0 gets a low score so a
    # different agent wins the next same-skill subtask.
    return 2 if idx == 0 else 5


def _decision_label(chosen: dict, candidates: list[dict], prev_winner: dict | None,
                    unconstrained_best: dict | None = None) -> str:
    """Short human-readable hiring reason for the UI."""
    if unconstrained_best and unconstrained_best["agent_id"] != chosen["agent_id"]:
        return "Budget Optimized"
    if prev_winner and prev_winner["agent_id"] != chosen["agent_id"]:
        return "Reputation-Driven Change"
    highest_rep = max(candidates, key=lambda c: c["reputation"])
    cheapest = min(candidates, key=lambda c: c["price_mon"])
    if chosen["agent_id"] == highest_rep["agent_id"] and chosen["agent_id"] != cheapest["agent_id"]:
        return "Highest Reputation"
    if chosen["agent_id"] == cheapest["agent_id"]:
        return "Best Value"
    return "Best Value"


def _build_reasoning(chosen: dict, candidates: list[dict], prev_winner: dict | None,
                     remaining: float = float("inf"), unconstrained_best: dict | None = None) -> str:
    """Deterministic, always-accurate manager reasoning that surfaces the
    cost-vs-quality tradeoff, a reputation-driven flip, and budget pressure."""
    others = [c for c in candidates if c["agent_id"] != chosen["agent_id"]]
    cheapest = min(candidates, key=lambda c: c["price_mon"])
    highest_rep = max(candidates, key=lambda c: c["reputation"])
    bits: list[str] = []

    # Budget note: the unconstrained best pick was unaffordable, so we traded down.
    if unconstrained_best and unconstrained_best["agent_id"] != chosen["agent_id"]:
        bits.append(
            f"{unconstrained_best['name']} has the highest reputation, but remaining budget "
            f"({max(remaining, 0.0):.3f} MON) is limited - selecting {chosen['name']} for better cost efficiency."
        )
        return " ".join(bits)

    # Flip note: previously preferred a different agent for this skill.
    if prev_winner and prev_winner["agent_id"] != chosen["agent_id"]:
        prev_now = next((c for c in candidates if c["agent_id"] == prev_winner["agent_id"]), prev_winner)
        bits.append(
            f"Previously hired {prev_now['name']}, but its reputation fell to "
            f"{prev_now['reputation']:.2f} after a weak rating, so switching to {chosen['name']}."
        )

    if chosen["agent_id"] == highest_rep["agent_id"] and chosen["agent_id"] != cheapest["agent_id"]:
        bits.append(
            f"Paying a premium ({chosen['price_mon']} MON) for {chosen['name']}'s top reputation "
            f"{chosen['reputation']:.2f} - quality wins here."
        )
    elif chosen["agent_id"] == cheapest["agent_id"] and others:
        rival = highest_rep if highest_rep["agent_id"] != chosen["agent_id"] else others[0]
        bits.append(
            f"{chosen['name']} gives the best value: rep {chosen['reputation']:.2f} at just "
            f"{chosen['price_mon']} MON vs {rival['name']} (rep {rival['reputation']:.2f} @ {rival['price_mon']} MON)."
        )
    else:
        bits.append(
            f"{chosen['name']} (rep {chosen['reputation']:.2f} @ {chosen['price_mon']} MON) "
            f"has the highest utility score {chosen['utility']:.3f}."
        )
    return " ".join(bits)


async def run_task(run_id: int, prompt: str) -> None:
    try:
        await bus.emit(run_id, "run_started", {"prompt": prompt})

        if chain.is_ready():
            try:
                bal = await asyncio.to_thread(chain.balance_mon)
                if bal < config.MIN_BALANCE_WARN_MON:
                    await bus.emit(run_id, "low_balance", {"balance_mon": round(bal, 4)})
            except Exception:
                pass

        # Workforce budget the human allocated for this run.
        with get_session() as s:
            run = s.get(Run, run_id)
            budget = float(run.budget_mon or 0.0)
        await bus.emit(run_id, "budget", {"budget": round(budget, 6), "spent": 0.0, "remaining": round(budget, 6)})

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
        last_winner_by_skill: dict[str, dict] = {}
        spent = 0.0
        for st in st_info:
            remaining = budget - spent if budget > 0 else float("inf")
            spent_this = await _run_subtask(
                run_id, st, context="\n".join(results), results=results,
                last_winner_by_skill=last_winner_by_skill, remaining=remaining,
            )
            spent += spent_this
            if budget > 0:
                await bus.emit(run_id, "budget_update", {
                    "budget": round(budget, 6),
                    "spent": round(spent, 6),
                    "remaining": round(max(budget - spent, 0.0), 6),
                })

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


async def _run_subtask(run_id: int, st: dict, context: str, results: list[str], last_winner_by_skill: dict, remaining: float = float("inf")) -> float:
    """Returns the MON spent on this subtask (0.0 if skipped over budget)."""
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
    await bus.emit(run_id, "candidates_evaluated", {"subtask_idx": st["idx"], "skill": st["skill"], "candidates": candidates})

    # 2. budget-aware selection: best utility AMONG agents we can still afford.
    unconstrained_best = candidates[0]
    eps = 1e-9
    affordable = [c for c in candidates if c["price_mon"] <= remaining + eps]

    if not affordable:
        # Nothing fits the remaining budget -> skip this subtask rather than overspend.
        cheapest = min(candidates, key=lambda c: c["price_mon"])
        note = (
            f"Skipping '{st['description'][:60]}': cheapest agent {cheapest['name']} costs "
            f"{cheapest['price_mon']} MON but only {max(remaining, 0.0):.3f} MON remains in budget."
        )
        with get_session() as s:
            s.add(Decision(subtask_id=st["id"], candidates_json=json.dumps(candidates), selected_agent_id=0, utility=0.0, reasoning=note))
            row2 = s.get(Subtask, st["id"])
            row2.status = "skipped"
            s.add(row2)
            s.commit()
        await bus.emit(run_id, "subtask_skipped", {"subtask_idx": st["idx"], "reason": note, "remaining": round(max(remaining, 0.0), 6)})
        return 0.0

    chosen = affordable[0]
    budget_limited = chosen["agent_id"] != unconstrained_best["agent_id"]

    prev_winner = last_winner_by_skill.get(st["skill"])
    if config.NARRATE_WITH_LLM:
        reasoning = await asyncio.to_thread(llm_service.narrate_decision, st["description"], candidates, chosen)
    else:
        reasoning = _build_reasoning(chosen, candidates, prev_winner, remaining=remaining, unconstrained_best=unconstrained_best if budget_limited else None)
    decision_label = _decision_label(chosen, candidates, prev_winner, unconstrained_best if budget_limited else None)
    last_winner_by_skill[st["skill"]] = chosen
    with get_session() as s:
        s.add(Decision(subtask_id=st["id"], candidates_json=json.dumps(candidates), selected_agent_id=chosen["agent_id"], utility=chosen["utility"], reasoning=reasoning))
        row2 = s.get(Subtask, st["id"])
        row2.status = "hiring"
        s.add(row2)
        s.commit()
    await bus.emit(run_id, "agent_selected", {"subtask_idx": st["idx"], "agent_id": chosen["agent_id"], "name": chosen["name"], "price_mon": chosen["price_mon"], "reputation": chosen["reputation"], "utility": chosen["utility"], "reasoning": reasoning, "decision_label": decision_label})

    # 3. pay on-chain
    await _pay(run_id, st, chosen)

    # 4. work
    persona = personas.get(chosen["agent_id"], "")
    work = await asyncio.to_thread(llm_service.do_work, persona, st["skill"], st["description"], context)
    results.append(f"### {st['description']}\n{work}")
    with get_session() as s:
        row2 = s.get(Subtask, st["id"])
        row2.status = "working"
        s.add(row2)
        s.commit()
    await bus.emit(run_id, "work_received", {"subtask_idx": st["idx"], "agent_id": chosen["agent_id"], "name": chosen["name"], "output": work})

    # 5. rate on-chain -> reputation changes the NEXT decision
    await _rate(run_id, st, chosen, work)

    return float(chosen["price_mon"])


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
        p.latency_ms = int(result.get("latency_ms", 0) or 0)
        s.add(p)
        sub = s.get(Subtask, st["id"])
        sub.status = "paid"
        s.add(sub)
        s.commit()
    await bus.emit(run_id, "payment_confirmed", {"subtask_idx": st["idx"], "agent_id": chosen["agent_id"], "amount_mon": chosen["price_mon"], "tx_hash": result.get("tx_hash", ""), "block": result.get("block", 0), "status": result.get("status", ""), "latency_ms": result.get("latency_ms", 0), "explorer": config.EXPLORER_TX_BASE + result.get("tx_hash", "") if result.get("tx_hash") else ""})
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
