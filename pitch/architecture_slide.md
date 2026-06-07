# Architecture Slide (for presentation)

## Title: Monad Agent Hackathon Kit

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                    │
│  Landing │ Dashboard │ Chat │ Marketplace │ Demo        │
└────────────────────────┬────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────┐
│                  BACKEND (FastAPI)                       │
│  /chat  /agent/run  /agent/workflow  /rag/query         │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ LLM Provider│  │ RAG Service  │  │ Agent Service │  │
│  │ OpenAI      │  │ Load→Chunk   │  │ Orchestration │  │
│  │ Anthropic   │  │ Embed→Retrieve│ │              │  │
│  │ OpenRouter  │  └──────────────┘  └───────┬───────┘  │
│  └─────────────┘                             │          │
└──────────────────────────────────────────────┼──────────┘
                                               │
┌──────────────────────────────────────────────▼──────────┐
│                   MULTI-AGENT LAYER                      │
│  Planner → Researcher → Critic → Executor → Wallet      │
└──────────────────────────────┬──────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────┐
│                   MONAD BLOCKCHAIN                       │
│  Agent Wallets │ Escrow │ Reputation Contract           │
└─────────────────────────────────────────────────────────┘
```

## Talking Points

- **Modular**: swap LLM provider via env var
- **Visible pipeline**: judges see agent steps, not black box
- **Blockchain optional depth**: wallet + reputation when time allows
