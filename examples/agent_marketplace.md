# Agent Marketplace

## Problem

Developers and businesses need specialized AI agents but have no trusted way to discover, pay for, and rate them.

## Solution

An on-chain agent marketplace on Monad where:
- Agents list services with wallet addresses and pricing
- Users pay in MON via escrow smart contract
- Reputation scores stored on-chain after task completion
- Multi-agent workflows orchestrated via the kit's pipeline

## Architecture

```
Frontend (Marketplace UI)
    ↓
FastAPI Backend (agent/workflow)
    ↓
Multi-Agent Pipeline (Planner → Executor)
    ↓
Wallet Agent → Monad Escrow Contract
    ↓
Reputation Contract (on-chain scores)
```

## Tech Stack

- Frontend: Next.js + WalletCard + AgentCard (included)
- Backend: FastAPI + workflow.py
- Blockchain: Monad testnet + Solidity escrow
- LLM: OpenAI/Anthropic via provider layer

## Demo Plan (5 min)

1. Browse marketplace — show 4 featured agents
2. Click ChainPilot → view wallet + reputation
3. Run workflow: "Analyze DeFi yield on Monad"
4. Show payment tx hash (testnet)
5. Reputation badge updates after task

## Judge Pitch

> "We built a trustless agent marketplace on Monad. Agents have wallets, get paid on-chain, and build verifiable reputation. Our multi-agent pipeline handles complex tasks autonomously — demo live in 30 seconds."
