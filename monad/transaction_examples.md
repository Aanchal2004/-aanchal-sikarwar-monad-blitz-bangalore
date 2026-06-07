# Monad Transaction Examples

## Send MON (ethers.js)

```javascript
const tx = await wallet.sendTransaction({
  to: "0xRecipientAddress",
  value: ethers.parseEther("0.01"),
});
const receipt = await tx.wait();
console.log("Tx hash:", receipt.hash);
```

## Sign Message (Agent Identity)

```javascript
const message = `Agent ${agentId} completed task ${taskId} at ${Date.now()}`;
const signature = await wallet.signMessage(message);
// Store signature on-chain or in reputation contract
```

## Call Smart Contract

```javascript
const abi = ["function recordTask(bytes32 agentId, uint8 rating) external"];
const contract = new ethers.Contract(CONTRACT_ADDRESS, abi, wallet);
const tx = await contract.recordTask(agentIdHash, 5);
await tx.wait();
```

## Gas & Error Handling

```javascript
try {
  const gas = await contract.recordTask.estimateGas(agentIdHash, 5);
  const tx = await contract.recordTask(agentIdHash, 5, { gasLimit: gas * 120n / 100n });
  await tx.wait();
} catch (e) {
  console.error("Tx failed:", e.message);
}
```

## Demo Flow

1. User hires agent from marketplace
2. Agent completes task via workflow
3. Wallet agent signs payment tx on Monad testnet
4. Show tx hash in DemoPanel for judges
