# Agent Reputation System

## Problem

AI agent marketplaces lack trust — users can't verify agent quality or prevent fake reviews.

## Solution

On-chain reputation where:
- Each agent has a registered wallet address
- Task completions emit events with client ratings
- Reputation score computed on-chain (average rating)
- Frontend displays ReputationBadge from contract data

## Architecture

```
Agent completes task
  → Client rates 1-5
  → Backend calls reputation contract
  → Event emitted: TaskCompleted(agentId, rating)
  → Frontend reads score via RPC
  → ReputationBadge updates
```

## Tech Stack

- Solidity: AgentReputation contract (monad/smart_contract_notes.md)
- Backend: wallet_agent + web3 call
- Frontend: ReputationBadge component
- Indexer (optional): listen to events for leaderboard

## Demo Plan

1. Show agent with 4.8 reputation
2. Complete a task via workflow
3. Submit rating in UI
4. Call contract — show tx hash
5. Refresh — badge updates to new score

## Judge Pitch

> "Trust is the bottleneck for agent marketplaces. We store reputation on Monad — tamper-proof, transparent, and composable. Any dApp can read our agent scores."
