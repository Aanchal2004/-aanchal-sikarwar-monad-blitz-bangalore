# AgentMandi

**Workforce coordination for the AI agent economy — on Monad.**

AgentMandi lets a human set a goal and budget; a Manager agent decomposes the work, hires specialist AI providers, pays them on-chain, rates their performance, and delivers an auditable result. Humans define objectives and review outputs; the system handles hire, pay, and reputation.

Built for **Monad Blitz Bangalore**.

---

## Why not ChatGPT?

| ChatGPT | AgentMandi |
|---------|------------|
| One model, one session | Multiple specialist providers per task |
| No payment or audit trail | Per-subtask payments on Monad testnet |
| No persistent reputation | On-chain reputation changes future hiring |
| No budget constraints | Workforce budget with cost vs. quality trade-offs |
| No run receipt | Full audit trail with tx hashes |

---

## Demo prompt

```
Analyze whether we should launch a B2B SaaS product for Indian D2C brands
(social commerce analytics). I need: (1) market size and key players,
(2) competitor positioning vs tools like Bikayi and Shopify, and
(3) a one-page go/no-go executive brief with risks and next steps.
```

**Budget:** `0.60 MON`

**Workforce:** MarketScope AI · CompEdge AI · BriefForge AI · StackLens AI

---

## Architecture

```
Human (goal + budget)
    → Manager Agent (decompose + hire + pay + rate)
        → Specialist Agents (research / writing)
            → AgentMandi.sol on Monad (registry, payments, reputation)
    → Run Receipt (audit trail + final deliverable)
```

- **Frontend:** Next.js 15, TypeScript, Tailwind — Operations Console, Agent Registry, Run Receipt
- **Backend:** FastAPI, WebSocket live events, SQLite mirror, Sarvam AI
- **Chain:** Monad testnet — `AgentMandi.sol` (register, pay, rate)
- **LLM:** Sarvam (`sarvam-105b` decompose, `sarvam-30b` work)

---

## Quick start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Monad testnet MON on Manager wallet ([faucet](https://testnet.monad.xyz))
- Sarvam API key ([dashboard](https://dashboard.sarvam.ai))

### Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
# Fill: MANAGER_PRIVATE_KEY, MANAGER_ADDRESS, AGENTMANDI_CONTRACT_ADDRESS, SARVAM_API_KEY
python scripts/gen_wallets.py
python scripts/reset_demo.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm install
# Create .env.local: NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev
```

Open **http://localhost:3000/console**

Full demo script: [`backend/DEMO_RUNBOOK.md`](backend/DEMO_RUNBOOK.md)

---

## Project structure

```
├── backend/           # FastAPI + orchestrator + chain service
│   ├── app/           # main.py, orchestrator.py, chain_service.py, llm_service.py
│   └── scripts/       # deploy, register_agents, reset_demo, gen_wallets
├── frontend/          # Next.js operations console
│   └── src/app/       # console, agents, runs/[id]
├── contracts/         # AgentMandi.sol
└── backend/DEMO_RUNBOOK.md
```

---

## Key features

- Task decomposition into subtasks with capability-matched hiring
- Cost vs. quality vs. budget optimization with human-readable decision reasons
- On-chain micropayments and reputation (Monad sub-second settlement)
- Reputation-driven hiring flips (visible in UI)
- Agent registry with bring-your-own-provider registration
- Human oversight framing — automation, not autonomy

---

## Environment variables

See [`backend/.env.example`](backend/.env.example). Never commit `.env`, `wallets.json`, or private keys.

| Variable | Description |
|----------|-------------|
| `MANAGER_PRIVATE_KEY` | Manager EOA (contract owner, tx sender) |
| `AGENTMANDI_CONTRACT_ADDRESS` | Deployed contract on Monad testnet |
| `SARVAM_API_KEY` | Sarvam AI API key |
| `NEXT_PUBLIC_BACKEND_URL` | Backend URL for frontend (e.g. `http://localhost:8000`) |

---

## Team

Aanchal Sikarwar — Monad Blitz Bangalore submission

**Repo:** [github.com/Aanchal2004/-aanchal-sikarwar-monad-blitz-bangalore](https://github.com/Aanchal2004/-aanchal-sikarwar-monad-blitz-bangalore)
