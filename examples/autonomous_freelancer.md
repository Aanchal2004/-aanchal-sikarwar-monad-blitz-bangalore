# Autonomous Freelancer Agent

## Problem

Freelancers spend hours on proposals, research, and deliverables. Clients can't verify AI-assisted work quality.

## Solution

An autonomous freelancer agent that:
- Accepts job descriptions via chat
- Plans, researches, drafts, and self-critiques deliverables
- Stores completed work hash on Monad for proof of completion
- Gets paid via agent wallet on task approval

## Architecture

```
Job Post (Chat UI)
  → Planner (break into deliverables)
  → Researcher (RAG on client docs)
  → Critic (quality gate)
  → Executor (final deliverable)
  → Wallet Agent (invoice + payment tx)
  → On-chain proof (content hash stored)
```

## Tech Stack

- Multi-agent workflow (agents/workflow.py)
- RAG for client document ingestion (datasets/)
- Monad for payment + proof storage
- ChatInterface for client interaction

## Demo Plan

1. Paste a fake "job posting" in chat
2. Run workflow — show 4 agent steps animating
3. Display final proposal/document
4. Show on-chain hash of deliverable
5. Simulate payment to agent wallet

## Judge Pitch

> "Our agent is an autonomous freelancer — it plans, researches, writes, and gets paid on Monad. Every deliverable is hashed on-chain for verifiable proof of work."
