# Smart Contract Notes

## Minimal Reputation Contract (Solidity sketch)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AgentReputation {
    struct Agent {
        uint256 score;      // cumulative rating * 100
        uint256 taskCount;
        address wallet;
    }

    mapping(bytes32 => Agent) public agents;

    event TaskCompleted(bytes32 indexed agentId, uint8 rating, address client);

    function registerAgent(bytes32 agentId, address wallet) external {
        agents[agentId].wallet = wallet;
    }

    function recordTask(bytes32 agentId, uint8 rating) external {
        require(rating <= 5, "max 5");
        Agent storage a = agents[agentId];
        a.score += rating * 100;
        a.taskCount += 1;
        emit TaskCompleted(agentId, rating, msg.sender);
    }

    function getAverage(bytes32 agentId) external view returns (uint256) {
        Agent storage a = agents[agentId];
        if (a.taskCount == 0) return 0;
        return a.score / a.taskCount / 100;
    }
}
```

## Agent Marketplace Escrow (sketch)

```solidity
mapping(bytes32 => uint256) public escrows;

function deposit(bytes32 taskId) external payable {
    escrows[taskId] += msg.value;
}

function release(bytes32 taskId, address agent) external {
    uint256 amount = escrows[taskId];
    escrows[taskId] = 0;
    payable(agent).transfer(amount);
}
```

## Deploy with Foundry

```bash
forge create src/AgentReputation.sol:AgentReputation \
  --rpc-url $MONAD_RPC_URL \
  --private-key $DEPLOYER_KEY
```

## On-Chain Identity

- `agentId = keccak256(agentName + walletAddress)`
- Store metadata (name, skills) off-chain (IPFS) or in events
- Reputation score on-chain for trustless marketplace
