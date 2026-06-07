# Monad Hackathon Playbook — AI × Monad Winning Strategy

> A decision document for **Monad Blitz Bangalore V4: The Agent Economy**. Built for an AI engineer (Python, LLMs, RAG, LangGraph) with limited blockchain experience. Goal: pick the highest-probability winning project and ship it in ~6 hours.
>
> Constraints baked in: ~6h build (11:30 → 17:15 freeze), **must deploy live on Monad Testnet**, 3-minute demo, judged 50% peer vote / 50% jury, rewarding **novelty + Monad-specific leverage** over polish.

---

## 1. What Unique Capabilities Does Monad Provide?

| Capability | What it means | Why it's unique |
|---|---|---|
| **Full EVM compatibility** | Same Solidity, bytecode, RPC, and tooling (Foundry, viem, ethers, MetaMask) as Ethereum | You reuse the entire Ethereum ecosystem with zero relearning — rare among "fast" chains |
| **High throughput (~10k TPS target)** | Parallel execution runs independent transactions concurrently | Makes high-frequency, many-agent activity viable |
| **Sub-second finality (~400ms blocks, ~800ms final)** | A transaction is irreversibly done in ~1s | Feels like a normal API call — enables interactive/agentic UX |
| **Cheap gas (sub-cent)** | Abundant fast block space | Micro-payments and frequent state writes become economical |
| **Native x402 support** | On-chain "HTTP 402 Payment Required" — pay-per-API-call in MON | Agents can pay per request with no card/subscription |
| **Account abstraction (ERC-4337, EIP-7702)** | Programmable wallets with spending rules, sponsored gas | Agents get safe, rule-bound autonomous wallets |
| **Agent identity standard (ERC-8004)** | On-chain, portable agent identity + reputation primitives | Purpose-built for the agent economy |

**The essence:** Monad is the only environment where you get Ethereum's tooling/security *and* the speed/cost profile that makes autonomous agents transacting continuously actually practical.

---

## 2. Which Capabilities Are Most Relevant to AI Agents?

Ranked by relevance to an AI-agent project:

1. **Payments (x402 + cheap gas)** — agents paying per tool-call or paying each other. *This is the headline of "The Agent Economy."*
2. **Identity (ERC-8004 + wallets)** — every agent is a verifiable, self-owned actor.
3. **Reputation (on-chain registry)** — trustless track records so agents/users can choose whom to hire.
4. **Coordination (smart contracts as neutral referee)** — escrow, marketplaces, task auctions without a central server.
5. **Ownership (tokens/NFTs)** — provable ownership of datasets, model outputs, licenses, deliverables.

The sub-second finality + low fees are the *enablers* that make all five usable at machine speed rather than theoretical.

---

## 3. What Applications Become Possible Because of Monad?

Things that are **impossible or impractical on Ethereum** but viable on Monad:

- **Pay-per-call AI APIs** — an agent pays $0.001 on-chain per inference/tool call (gas would dwarf the payment on Ethereum).
- **Live agent marketplaces** — bids, matches, and settlements happen in seconds, not minutes.
- **Per-task reputation updates** — write a rating after *every* interaction without cost concerns.
- **Real-time multi-agent economies** — dozens of agents transacting concurrently (parallel execution prevents bottlenecks).
- **Interactive on-chain consumer apps** — sub-second feedback loops that feel like a normal web app.
- **Streaming micropayments** — pay an agent continuously as work progresses.

---

## 4. Strongest AI × Monad Project Ideas

Eight candidates, each scored later. Format: Problem · Why existing solutions fall short · Why Monad helps · MVP scope · Demo flow · Effort · Risk.

### Idea A — Agent Reputation Network (on-chain trust registry)
- **Problem:** You can't tell which AI agent/tool is reliable; reviews are siloed and fakeable.
- **Why existing solutions fall short:** Platform reviews are centralized, gameable, and non-portable across apps.
- **Why Monad helps:** Tamper-proof, public, composable reputation; cheap enough to update after every task; sub-second so the UI feels live.
- **MVP scope:** A `ReputationRegistry` contract (`recordTask(agentId, rating)`, `getScore`), backend writes ratings, frontend `ReputationBadge` reads on-chain.
- **Demo flow:** Run a task → rate the agent → tx on testnet → badge updates live from chain.
- **Effort:** Low-Medium (one small contract + read/write wiring — your kit already has the UI).
- **Risk:** Low.

### Idea B — AI Research / Task Marketplace with escrow
- **Problem:** No trustless way to hire a specialized agent and guarantee payment-on-delivery.
- **Why existing solutions fall short:** Freelance platforms take cuts, hold funds, and can censor; no neutral escrow.
- **Why Monad helps:** Escrow contract is a neutral referee; fast settlement; many small jobs become economical.
- **MVP scope:** `Escrow` contract (`deposit(taskId)`, `release(taskId, agent)`), marketplace UI (your kit has it), workflow produces the deliverable.
- **Demo flow:** Post task + deposit MON → agent pipeline delivers → release escrow → agent paid on-chain.
- **Effort:** Medium.
- **Risk:** Medium (two-sided flow to demo).

### Idea C — Pay-Per-Call AI API via x402 (agentic payments)
- **Problem:** Agents can't pay for tools/APIs autonomously — everything needs a human's credit card/subscription.
- **Why existing solutions fall short:** API keys + billing assume a human account; no native per-call settlement.
- **Why Monad helps:** **x402 is natively supported** — pay-per-request in MON, settled in <1s, sub-cent gas.
- **MVP scope:** Wrap one AI endpoint (e.g., RAG query) behind an x402 paywall; agent wallet pays per call; show payment + response.
- **Demo flow:** Agent requests answer → 402 Payment Required → agent auto-pays MON → gets the RAG answer → show tx on explorer.
- **Effort:** Medium (x402 integration is the learning curve).
- **Risk:** Medium-High (newest tech; highest novelty/payoff).

### Idea D — Autonomous Freelancer Agent (self-employed agent)
- **Problem:** Agents can do work but can't get hired, paid, or prove what they delivered.
- **Why existing solutions fall short:** No identity + payment + proof in one loop.
- **Why Monad helps:** Wallet identity + instant payment + on-chain deliverable hash = a complete economic actor.
- **MVP scope:** Your Planner→Researcher→Critic→Executor pipeline + wallet agent that invoices and stores a deliverable hash.
- **Demo flow:** Give a job → pipeline runs → deliverable produced → hash + payment recorded on testnet.
- **Effort:** Medium (mostly your existing kit + a tiny contract).
- **Risk:** Low-Medium.

### Idea E — Multi-Agent Economy (agents hiring agents)
- **Problem:** Multi-agent systems lack a neutral settlement + coordination layer across orgs.
- **Why existing solutions fall short:** Central orchestrators everyone must trust; no real value exchange.
- **Why Monad helps:** Contract as referee; parallel execution handles concurrent agents; cheap settlement.
- **MVP scope:** 2–3 specialized agents, each with a wallet, paying each other for sub-tasks via a settlement contract.
- **Demo flow:** Orchestrator hires Researcher (pays) → Researcher hires Summarizer (pays) → all settled on-chain.
- **Effort:** Medium-High.
- **Risk:** Medium-High (most moving parts to demo in 3 min).

### Idea F — On-chain Agent Identity Passport (ERC-8004)
- **Problem:** No portable, verifiable identity for agents across platforms.
- **Why existing solutions fall short:** `agent_id` strings in private DBs aren't verifiable or portable.
- **Why Monad helps:** ERC-8004 gives a native standard; sub-second registration; composable with reputation.
- **MVP scope:** Register agents under ERC-8004, show a public "passport" page reading identity + reputation from chain.
- **Demo flow:** Mint agent identity → other agent/user verifies it on-chain → passport page renders live.
- **Effort:** Medium.
- **Risk:** Medium (standard learning curve).

### Idea G — RAG Provenance / "Verified Answers"
- **Problem:** You can't trust or audit where an AI answer came from.
- **Why existing solutions fall short:** Answers are ephemeral; no proof of sources or who answered.
- **Why Monad helps:** Hash the answer + sources + agent identity on-chain → auditable provenance; cheap per-answer writes.
- **MVP scope:** RAG pipeline (in your kit) + write `(queryHash, answerHash, agentId)` on-chain; verify page.
- **Demo flow:** Ask question → get sourced answer → proof written on testnet → anyone verifies later.
- **Effort:** Low-Medium.
- **Risk:** Low (but novelty is moderate).

### Idea H — Prediction/Bounty Market for Agent Tasks
- **Problem:** No market signal for which agent tasks are valuable.
- **Why existing solutions fall short:** Centralized bounty boards, slow payouts.
- **Why Monad helps:** Fast, cheap on-chain bounties + instant payout on completion.
- **MVP scope:** Bounty contract + agent that claims and completes → auto-payout.
- **Effort:** Medium.
- **Risk:** Medium.

---

## 5. Which Ideas Are Realistic in a 1-Day Hackathon?

| Idea | Realistic in ~6h? | Notes |
|---|---|---|
| A — Reputation Network | ✅ Strong | One small contract; kit UI ready |
| B — Marketplace + Escrow | ✅ Good | Two-sided but well-scoped |
| C — x402 Pay-Per-Call | ⚠️ If you timebox x402 learning | Highest novelty; have a mock fallback |
| D — Autonomous Freelancer | ✅ Strong | Mostly your existing kit |
| E — Multi-Agent Economy | ⚠️ Tight | Impressive but many parts to demo |
| F — ERC-8004 Passport | ⚠️ Medium | Depends on standard tooling availability |
| G — RAG Provenance | ✅ Strong | Simple contract + your RAG |
| H — Bounty Market | ⚠️ Medium | Doable but less differentiated |

**Realistic + high-leverage shortlist:** A, B, C, D, G.

---

## 6. Best Balance (Feasibility × Demo × Judge Appeal × Monad Alignment)

Scored 1–5 (5 = best). "Monad alignment" = is the chain load-bearing + does it use Monad-specific strengths.

| Idea | Feasibility | Demo Quality | Judge Appeal | Monad Alignment | **Total** |
|---|:---:|:---:|:---:|:---:|:---:|
| **C — x402 Pay-Per-Call** | 3 | 5 | 5 | 5 | **18** |
| **B — Marketplace + Escrow** | 4 | 5 | 4 | 5 | **18** |
| **D — Autonomous Freelancer** | 5 | 4 | 4 | 4 | **17** |
| **A — Reputation Network** | 5 | 4 | 4 | 4 | **17** |
| **E — Multi-Agent Economy** | 3 | 5 | 5 | 4 | **17** |
| **G — RAG Provenance** | 5 | 3 | 3 | 4 | **15** |
| **F — ERC-8004 Passport** | 3 | 3 | 4 | 5 | **15** |
| **H — Bounty Market** | 3 | 4 | 3 | 4 | **14** |

---

## Top 5 Highest Probability Winning Ideas

### #1 — Agentic Pay-Per-Call AI Service (x402) 🏆
*The purest expression of "The Agent Economy." An AI agent autonomously pays MON per API/tool call via x402.*
- **Why judges may like it:** Directly nails the theme; "an agent that pays for itself" is a memorable, novel wow-moment; uses Monad's flagship agent feature.
- **Why Monad is required:** x402 is natively supported and only economical with sub-cent gas + sub-second settlement. On Ethereum the gas would exceed the payment and the latency would kill the UX.
- **How an AI engineer builds it fast:** Keep one paid endpoint (your `/rag/query`). Put it behind an x402 paywall using Monad's x402 proxy contracts (already deployed on testnet). Give the agent a funded wallet that auto-pays on `402`. Have a **mock-payment fallback** if x402 wiring runs long — still demo the flow.

### #2 — Trustless Agent Marketplace with Escrow
*Hire a specialized agent; funds are held in escrow and released on delivery — all on-chain.*
- **Why judges may like it:** Complete, relatable economic loop; strong live demo (deposit → work → payout); your kit already has the marketplace UI.
- **Why Monad is required:** Neutral escrow contract replaces a trusted platform; fast settlement makes many small jobs viable.
- **How to build fast:** Minimal `Escrow` contract (`deposit`/`release`). Wire your existing marketplace + workflow. Deploy with Foundry to testnet. Show the agent getting paid.

### #3 — Autonomous Freelancer Agent
*An agent that accepts a job, runs Planner→Researcher→Critic→Executor, delivers, invoices, and records proof-of-work on-chain.*
- **Why judges may like it:** "A self-employed AI" is a clean narrative; your multi-agent pipeline already animates beautifully in the Demo page.
- **Why Monad is required:** Identity + instant payment + immutable deliverable hash form a real economic actor; cheap enough to record every job.
- **How to build fast:** ~90% is your existing kit. Add a tiny contract storing `(jobId, deliverableHash, agentWallet)` and a payment tx. Mostly wiring, not new code.

### #4 — On-chain Agent Reputation Network
*Every completed task updates a public, tamper-proof reputation score that drives agent selection.*
- **Why judges may like it:** Solves the real "which agent do I trust?" problem; composable primitive others could build on; live badge updates.
- **Why Monad is required:** Per-task writes are only affordable with cheap gas; sub-second finality makes the badge update feel instant.
- **How to build fast:** One `ReputationRegistry` contract; backend writes ratings; `ReputationBadge` reads from chain. Pairs naturally with #2 or #3 as an add-on.

### #5 — Multi-Agent Economy (agents hiring agents)
*An orchestrator agent hires sub-agents, each with a wallet, settling payments between them on-chain.*
- **Why judges may like it:** The most "wow" / futuristic demo — a visible economy of AIs; highest novelty ceiling.
- **Why Monad is required:** Parallel execution handles concurrent agent txs; neutral settlement layer; cheap inter-agent micropayments.
- **How to build fast:** Reuse your agents; give 2–3 of them wallets; one settlement contract; script the chain of hires. Highest risk — only attempt if comfortable, and pre-script the demo.

---

## If I Only Have 6 Hours

### Recommended project: **"PayPerThought" — an Autonomous Freelancer Agent that gets paid per task via x402 on Monad**

This fuses **#1 (x402 payments)** and **#3 (autonomous freelancer)** — the theme's bullseye, while leaning ~80% on your existing kit so you spend your 6 hours on the *novel, judge-impressing* part: an AI agent that earns money autonomously. Start with the freelancer loop (guaranteed working demo), then layer x402 as the wow-factor.

### Architecture

```
┌──────────────────────────── Frontend (Next.js — your kit) ───────────────────────────┐
│  Demo page: enter a job → watch pipeline → see payment tx + deliverable proof          │
└───────────────┬───────────────────────────────────────────────────────────────────────┘
                │ REST
┌───────────────▼─────────────── Backend (FastAPI — your kit) ──────────────────────────┐
│  /agent/workflow  →  Planner → Researcher → Critic → Executor (your multi-agent code)  │
│  /pay (x402)      →  paid wrapper around the deliverable; agent wallet auto-pays        │
│  wallet_agent     →  signs tx, records proof on-chain                                   │
└───────────────┬───────────────────────────────────────────────────────────────────────┘
                │ JSON-RPC (testnet-rpc.monad.xyz, chainId 10143)
┌───────────────▼─────────────────── Monad Testnet ──────────────────────────────────────┐
│  Agent wallet (funded via faucet.monad.xyz)                                             │
│  x402 proxy (native, already deployed)  +  tiny ProofOfWork contract                    │
│      ProofOfWork.record(jobId, deliverableHash, agentWallet)  → emits event             │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Tech Stack
- **Frontend:** Next.js + Tailwind (your kit) — Demo page + WalletCard + a tx/explorer link.
- **Backend:** FastAPI + your agent pipeline (LangGraph optional upgrade).
- **LLM:** OpenAI/OpenRouter via your provider abstraction (mock mode works if keys fail).
- **Chain:** Monad Testnet (chainId `10143`, RPC `testnet-rpc.monad.xyz`), Foundry to deploy.
- **Web3:** `viem` or `ethers` (Node) called from the backend, or `web3.py`. x402 via Monad's testnet x402 proxy contracts.
- **Contract:** ~20-line `ProofOfWork.sol` (a mapping + event). Keep it tiny.

### Demo Story (3 minutes — fits the official format)
1. **(20s) Hook:** "Meet an AI freelancer that earns its own money. You give it a job; it works, delivers, and gets paid on Monad — no human in the loop."
2. **(90s) Live:** Type a job on the Demo page → watch Planner→Researcher→Critic→Executor run → deliverable appears → agent's x402 payment fires → show the **tx on testnet.monadvision.com** and the deliverable hash recorded on-chain.
3. **(30s) How:** "Multi-agent pipeline in FastAPI, paid per task via Monad's native x402, proof-of-work stored on testnet. The chain is what lets an agent transact autonomously, instantly, for fractions of a cent."
4. **(20s) Why Monad:** "This only works because Monad gives us sub-second finality, sub-cent gas, and native x402 — impossible on Ethereum."
5. **(backup):** Screenshots + a 30s screen recording in case testnet hiccups.

### Judge Pitch (one-liner)
> "PayPerThought is a self-employed AI agent: it does the work, invoices itself, and gets paid per task on Monad via x402 — the agent economy, live on testnet."

### Stretch Goals (only if ahead of schedule)
1. **Reputation (Idea #4):** record a rating per job → live `ReputationBadge` from chain.
2. **Marketplace framing (Idea #2):** list multiple freelancer agents the user can choose.
3. **Agent-to-agent (Idea #5):** the freelancer pays a sub-agent (Summarizer) out of its earnings — a mini economy.
4. **ERC-8004 identity:** register the agent's identity as a verifiable passport.

### Risk Management
- **Biggest risk = x402 wiring time.** Mitigation: build the freelancer loop + a `/pay` *mock* first (fully working demo by hour 4), then attempt real x402 (hours 4–5.5). If x402 lands, swap it in; if not, demo the mock and *say* it's x402-ready.
- **Testnet flakiness:** deploy early (by hour 3), keep the faucet-funded wallet ready, record a backup video.
- **Scope creep:** stretch goals are strictly optional. A clean 3-minute core loop beats five half-features — exactly what the judging criteria reward.

---

### Sources informing this playbook
- Monad docs: architecture, network/testnet info, x402 guide, ERC-8004 guide, EIP-7702 — https://docs.monad.xyz
- Monad Blitz Bangalore V4 event pack, Rules & Guidelines, Judging Process & Criteria, Demo prep, Resources (Notion)
- Companion file: `docs/monad_preread.md`
