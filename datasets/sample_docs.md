# Sample documents for RAG ingestion during hackathon.
# Add your own .txt or .md files here and call index_documents() with the path.

## Monad Overview

Monad is a high-performance EVM-compatible Layer 1 blockchain.
It supports parallel execution for high throughput and low latency.
Standard Ethereum tooling works: MetaMask, Foundry, Hardhat, ethers.js, viem.

## Agent Wallets

AI agents can hold dedicated wallets on Monad testnet.
Use environment variables for private keys — never expose in frontend code.
Agent wallets can sign transactions autonomously when given scoped permissions.

## Reputation On-Chain

Store agent reputation scores in a simple smart contract mapping:
agentId => { score, taskCount, lastUpdated }
Emit events on each task completion for indexers to track.
