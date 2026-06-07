# Monad Wallet Examples

## Create Wallet (ethers.js v6)

```javascript
import { Wallet, JsonRpcProvider } from "ethers";

const provider = new JsonRpcProvider(process.env.MONAD_RPC_URL);
const wallet = Wallet.createRandom().connect(provider);

console.log("Address:", wallet.address);
// Store wallet.privateKey in AGENT_WALLET_PRIVATE_KEY — NEVER in frontend
```

## Create Wallet (viem)

```typescript
import { createWalletClient, http } from "viem";
import { privateKeyToAccount, generatePrivateKey } from "viem/accounts";

const account = privateKeyToAccount(generatePrivateKey());
const client = createWalletClient({
  account,
  transport: http("https://testnet-rpc.monad.xyz"),
});
```

## Load Existing Agent Wallet

```javascript
import { Wallet } from "ethers";

const wallet = new Wallet(process.env.AGENT_WALLET_PRIVATE_KEY, provider);
const balance = await provider.getBalance(wallet.address);
```

## Agent Ownership Pattern

- Each agent gets a dedicated wallet address
- Human operator holds admin key for funding
- Agent signs txs within scoped limits (max amount, allowed contracts)
- Display wallet address on Agent Profile page for transparency

## Hackathon Tips

- Use testnet faucet for MON tokens
- Show wallet address + balance in demo UI (WalletCard component)
- Mock txs if faucet is slow — show "simulated" badge
