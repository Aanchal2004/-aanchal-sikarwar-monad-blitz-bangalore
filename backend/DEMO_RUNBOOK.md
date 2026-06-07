# AgentMandi — Demo Runbook

## Before EVERY rehearsal or live demo

```powershell
# 1. Navigate to backend/
cd "C:\Users\aanch\Desktop\monad hackathon\backend"

# 2. Reset to pristine on-chain baseline (fresh contract + seeded reputations)
#    MarketScope: 4.50 rep @ 0.05 MON  |  CompEdge: 5.00 rep @ 0.20 MON  |  BriefForge: 4.33 rep @ 0.10 MON
.\.venv\Scripts\python.exe scripts\reset_demo.py

# 3. Start backend (MUST restart to pick up new contract address)
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# You should see:  ✓  Demo baseline OK — MarketScope 4.50, CompEdge 5.00

# 4. In a separate terminal, start frontend
cd "C:\Users\aanch\Desktop\monad hackathon\frontend"
npm run dev

# 5. Open http://localhost:3000
```

## What the canonical demo shows

1. Submit (headline prompt):
   **"Analyze whether we should launch a B2B SaaS product for Indian D2C brands (social commerce analytics). I need: (1) market size and key players, (2) competitor positioning vs tools like Bikayi and Shopify, and (3) a one-page go/no-go executive brief with risks and next steps."**
   Budget: **0.60 MON**
2. Manager decomposes → 2 research subtasks + 1 writing subtask
3. **Subtask 1** (market sizing): **MarketScope AI** hired (*Best Value*) → 0.05 MON paid on-chain ✓
4. MarketScope rated **2/5** → reputation drops **4.50 → 3.67** on-chain
5. **Subtask 2** (competitive positioning): **FLIP** — **CompEdge AI** hired (*Reputation-Driven Change*) → 0.20 MON paid ✓
6. **Subtask 3** (go/no-go brief): **BriefForge AI** hired → 0.10 MON paid ✓
7. Final result: full research brief + Run Receipt with all tx hashes

**The judge moment**: *"These AI agents hired and paid each other — and changed who they hired because of on-chain reputation. That all just happened on Monad, for 0.35 MON, in under 30 seconds."*

## Workforce budget — two demo scenarios

Every run takes a **Workforce Budget** (MON). The Manager hires the best agent it can afford within the remaining budget; if nothing fits, it skips the subtask rather than overspending.

| Scenario | Budget | What it shows (validated on-chain) |
|---|---|---|
| **Default (keeps the flip)** | **0.60 MON** | Full canonical run. The reputation flip still fires (Bhavna, the expensive pick, stays affordable). ~58% budget used, comfortable remainder. |
| **Constrained (budget overrides quality)** | **0.20 MON** | After Asha's 0.05 spend, only 0.15 remains so Bhavna (0.20) is unaffordable. The Manager **trades down for cost efficiency** and the reasoning cites the budget verbatim: *"Bhavna has the highest reputation, but remaining budget (0.150 MON) is limited - selecting Asha for better cost efficiency."* Ends at 100% budget utilization. |
| **Over-constrained (skip)** | **~0.30 MON with 4 subtasks** | If decomposition yields 4 subtasks and budget runs out, the trailing subtask is **skipped** ("Skipped - over budget") rather than overspending. |

Use 0.60 for the headline reputation-flip demo. Use 0.20 for the budget-override demo — it is a *separate* lever and will suppress the flip. Note Sarvam decomposition is non-deterministic (usually 3 subtasks), so exact remainders vary slightly.

## Positioning — automation, not autonomy

> AgentMandi automates workforce **coordination**, not business ownership, governance, or strategic decision-making.
>
> The human remains responsible for **goals, incentives, budgets, governance, and final approval**. The model is: Human defines objective + budget → AgentMandi manages execution (hire, pay, rate) → Human reviews the deliverable.

This is reflected in the UI: the console shows the Human vs AgentMandi responsibilities split and a live budget bar; the Run Receipt opens with a Human Oversight section and an "Awaiting Human Review" badge.

## If you see the preflight WARNING on startup

Reputations are drifted from demo baseline. The flip will not happen. Run:
```
python scripts/reset_demo.py  →  restart uvicorn
```

## Environment

| Key | Value |
|---|---|
| LLM_PROVIDER | `sarvam` for demo, `mock` for dev |
| SCRIPTED_RATINGS | `true` (guarantees the flip) |
| NARRATE_WITH_LLM | `false` (free + always accurate) |
| Backend | http://localhost:8000 |
| Frontend | http://localhost:3000 |
| Contract | auto-written to .env by reset_demo.py |
| Explorer | https://testnet.monadexplorer.com |

## Credit budget (Sarvam)

~5 calls per run (1 decompose + ~4 work). 100 credits = ~20 runs.
