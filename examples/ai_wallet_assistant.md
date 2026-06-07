# AI Wallet Assistant

## Problem

Users struggle to manage crypto wallets, understand transactions, and delegate safe automated payments to AI.

## Solution

A wallet assistant agent that:
- Checks balances and explains transactions in plain English
- Executes scoped payments (e.g., max 0.1 MON per task)
- Signs messages for agent identity verification
- Runs on Monad testnet with full demo UI

## Architecture

```
User: "Pay the researcher agent 0.02 MON"
  → Chat → wallet_agent
  → Validate amount < daily limit
  → Build + sign transaction
  → Return tx hash + explorer link
  → WalletCard shows updated balance
```

## Tech Stack

- wallet_agent.py + wallet_agent.txt prompt
- ethers.js or web3.py for signing
- WalletCard component
- Monad testnet RPC

## Demo Plan

1. Show WalletCard with balance
2. Chat: "Send 0.01 MON to agent 0x..."
3. Agent validates and signs
4. Display tx hash in chat
5. Balance updates (or show simulated)

## Judge Pitch

> "We built an AI wallet assistant on Monad — natural language to on-chain actions, with safety limits. Ask it to pay an agent, check balance, or sign a message. Live on testnet."
