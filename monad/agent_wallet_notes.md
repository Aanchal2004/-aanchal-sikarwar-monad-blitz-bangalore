# Agent Wallet Notes

## Architecture

```
User Wallet ──pays──▶ Agent Wallet ──executes──▶ Smart Contract
                           │
                           └── signs task proofs
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| Agent Wallet | Dedicated EOA for each agent |
| Scoped Permissions | Limit max spend, allowed contract addresses |
| Task Escrow | User deposits MON; released on completion |
| Identity | Wallet address = on-chain agent ID |

## Security Rules (Hackathon)

1. **Never** put private keys in frontend or git
2. Use `.env` for `AGENT_WALLET_PRIVATE_KEY`
3. Testnet only during hackathon
4. Simulate txs if network is unstable

## Integration Points in This Kit

- `agents/wallet_agent.py` — agent logic
- `prompts/wallet_agent.txt` — system prompt
- `frontend/src/components/WalletCard.tsx` — UI display
- `backend/config/settings.py` — `MONAD_RPC_URL`, `AGENT_WALLET_PRIVATE_KEY`

## TODO for Hackathon

- [ ] Connect wallet_agent to ethers.js via Node subprocess or Python web3
- [ ] Add escrow contract (simple Solidity mapping)
- [ ] Emit events for reputation indexer
