# Monad Agent Hackathon Kit

**Ship AI agents + blockchain MVPs in one day.** A reusable starter repository for [Monad Blitz Bangalore](https://monad.xyz) — optimized for 6-8 hour hackathon sprints.

Build agent marketplaces, multi-agent systems, RAG apps, wallet agents, and on-chain reputation — fast.

---

## Project Structure

```
monad-agent-hackathon-kit/
├── frontend/          # Next.js + TypeScript + Tailwind + shadcn-style UI
├── backend/           # FastAPI + LangChain/LangGraph hooks
├── agents/            # Multi-agent framework (Planner → Executor pipeline)
├── prompts/           # Reusable system prompts for each agent
├── docs/              # Cheat sheets (FastAPI, LangChain, RAG, MCP, etc.)
├── datasets/          # Sample docs for RAG ingestion
├── scripts/           # Startup and health-check scripts
├── monad/             # Blockchain notes (wallets, txs, contracts)
├── pitch/             # Demo script, elevator pitch, submission template
├── examples/          # Hackathon idea templates with architecture
├── deployments/       # Vercel, Render, Railway, Docker guides
├── tests/             # API smoke tests
├── .env.example       # Environment variable template
├── docker-compose.yml
├── Makefile
└── README.md
```

---

## Quick Start

### Prerequisites

- **Node.js** 20+
- **Python** 3.11+
- **npm** or **pnpm**
- At least one LLM API key (optional — mock mode works without keys)

### 1. Setup

```bash
# Clone / enter project
cd "monad hackathon"

# Copy environment file
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux

# Install dependencies
make install
# Or manually:
# cd backend && pip install -r requirements.txt
# cd frontend && npm install
```

### 2. Configure Environment

Edit `.env` and set at minimum:

```env
LLM_PROVIDER=openai          # openai | anthropic | openrouter
OPENAI_API_KEY=sk-...        # or ANTHROPIC_API_KEY / OPENROUTER_API_KEY
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run

**Windows (PowerShell):**
```powershell
.\scripts\start.ps1
```

**Two terminals:**
```bash
make backend    # http://localhost:8000
make frontend   # http://localhost:3000
```

**Docker:**
```bash
docker compose up --build
```

### 4. Verify

| URL | Description |
|-----|-------------|
| http://localhost:3000 | Frontend landing page |
| http://localhost:8000/docs | FastAPI Swagger UI |
| http://localhost:3000/demo | Multi-agent workflow demo |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | `openai`, `anthropic`, or `openrouter` | `openai` |
| `LLM_MODEL` | Model name | `gpt-4o-mini` |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `ANTHROPIC_API_KEY` | Anthropic API key | — |
| `OPENROUTER_API_KEY` | OpenRouter API key | — |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend | `http://localhost:8000` |
| `MONAD_RPC_URL` | Monad testnet RPC | `https://testnet-rpc.monad.xyz` |
| `MONAD_CHAIN_ID` | Chain ID | `10143` |
| `AGENT_WALLET_PRIVATE_KEY` | Agent wallet (testnet only!) | — |

See `.env.example` for the full list.

---

## Frontend

**Stack:** Next.js 15, TypeScript, TailwindCSS, shadcn-style components

### Pages

| Route | Description |
|-------|-------------|
| `/` | Landing page |
| `/dashboard` | Stats, wallet, quick actions |
| `/chat` | Chat interface → `POST /chat` |
| `/marketplace` | Agent marketplace grid |
| `/agents/[id]` | Agent profile + chat |
| `/demo` | Live multi-agent workflow |

### Components

`ChatInterface`, `AgentCard`, `WalletCard`, `ReputationBadge`, `LoadingSpinner`, `Navbar`, `Sidebar`, `DemoPanel`

```bash
cd frontend
npm run dev      # Development
npm run build    # Production build
```

---

## Backend

**Stack:** FastAPI, Pydantic, LangChain/LangGraph (hooks), OpenAI/Anthropic/OpenRouter

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check + provider info |
| POST | `/chat` | Chat with LLM |
| POST | `/agent/run` | Run single agent |
| POST | `/agent/workflow` | Full multi-agent pipeline |
| POST | `/rag/query` | RAG question answering |

### Example Requests

```bash
# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'

# Run workflow
curl -X POST http://localhost:8000/agent/workflow \
  -H "Content-Type: application/json" \
  -d '{"query":"Build an agent marketplace on Monad"}'

# RAG query
curl -X POST http://localhost:8000/rag/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Monad?"}'
```

```bash
cd backend
uvicorn app:app --reload --port 8000
```

---

## Agent Workflow

```
User Query
    ↓
Planner Agent      → decomposes goal into steps
    ↓
Researcher Agent   → gathers context (RAG-ready)
    ↓
Critic Agent       → quality review + approval
    ↓
Executor Agent     → final deliverable
    ↓
Final Output
```

**Files:** `agents/workflow.py`, `agents/planner_agent.py`, etc.

**Upgrade to LangGraph:** See `agents/workflow.py` → `build_langgraph_workflow()` and `docs/langgraph_cheatsheet.md`.

---

## RAG Workflow

```
Documents (datasets/) → Load → Chunk → Embed → Store → Retrieve → Generate
```

**Implementation:** `backend/services/rag_service.py`

Add your docs to `datasets/` and restart the backend (auto-indexes on startup).

---

## Model Provider Abstraction

Switch LLM provider via environment variable — no code changes:

```env
LLM_PROVIDER=openai       # Uses OpenAI SDK
LLM_PROVIDER=anthropic    # Uses Anthropic SDK
LLM_PROVIDER=openrouter   # Uses OpenAI-compatible OpenRouter API
```

**Implementation:** `backend/services/llm_provider.py`

Without API keys, all endpoints return helpful mock responses so you can demo UI immediately.

---

## Monad Integration Points

| Component | Location |
|-----------|----------|
| Wallet agent | `agents/wallet_agent.py` |
| Wallet UI | `frontend/src/components/WalletCard.tsx` |
| Config | `backend/config/settings.py` |
| Wallet examples | `monad/wallet_examples.md` |
| Transaction examples | `monad/transaction_examples.md` |
| Smart contract sketches | `monad/smart_contract_notes.md` |
| Resources | `monad/monad_resources.md` |

---

## Hackathon Ideas

Pre-written templates in `examples/`:

- **Agent Marketplace** — discover, pay, rate agents on-chain
- **Autonomous Freelancer** — multi-agent job completion + payment
- **Agent Reputation System** — on-chain trust scores
- **AI Wallet Assistant** — natural language → Monad transactions
- **Multi-Agent Network** — visible pipeline demo (fastest to ship)

Each includes problem, solution, architecture, demo plan, and judge pitch.

---

## Deployment

| Platform | Guide |
|----------|-------|
| Vercel (frontend) | `deployments/vercel.md` |
| Render (backend) | `deployments/render.md` |
| Railway (full stack) | `deployments/railway.md` |
| Docker | `deployments/docker.md` |

**Recommended hackathon stack:** Railway (backend) + Vercel (frontend)

---

## Testing

```bash
cd backend
pip install -r ../tests/requirements.txt
python -m pytest ../tests/ -v
```

---

## Documentation

| Cheat Sheet | Topic |
|-------------|-------|
| `docs/fastapi_cheatsheet.md` | FastAPI patterns |
| `docs/langchain_cheatsheet.md` | LangChain RAG + chains |
| `docs/langgraph_cheatsheet.md` | Multi-agent graphs |
| `docs/rag_cheatsheet.md` | RAG pipeline |
| `docs/mcp_cheatsheet.md` | Model Context Protocol |
| `docs/prompt_engineering_cheatsheet.md` | Prompt tips |
| `docs/hackathon_workflow_guide.md` | Hour-by-hour plan |

---

## Pitch Materials

- `pitch/elevator_pitch.md` — 30-second pitch
- `pitch/demo_script.md` — 5-minute live demo script
- `pitch/architecture_slide.md` — presentation diagram
- `pitch/judging_checklist.md` — pre-submission checklist
- `pitch/final_submission_template.md` — submission form

---

## License

MIT — use freely for hackathons and learning.

**Good luck at Monad Blitz Bangalore! 🚀**
