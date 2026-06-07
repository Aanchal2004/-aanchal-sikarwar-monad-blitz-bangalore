// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title AgentMandi
/// @notice Minimal neutral coordinator for an autonomous AI agent workforce.
///         Holds agent identity, price, and reputation, and routes payments.
///         Owner (the Manager backend) registers agents, pays them, and rates
///         completed jobs. Payments flow THROUGH this contract so every transfer
///         emits a verifiable on-chain event. No tokenomics, no escrow release
///         logic, no upgradeability -- deliberately tiny.
contract AgentMandi {
    struct Agent {
        address wallet;     // payout address
        uint256 pricePerJob; // wei
        uint64 ratingSum;   // sum of scores (1..5)
        uint64 jobs;        // number of rated jobs
        bool active;
    }

    address public owner;
    mapping(uint256 => Agent) public agents; // agentId => Agent

    event AgentRegistered(uint256 indexed id, address wallet, uint256 pricePerJob);
    event Paid(uint256 indexed id, address indexed from, address indexed to, uint256 amount, uint256 jobId);
    event ReputationUpdated(uint256 indexed id, uint256 avgX100, uint64 jobs);

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function registerAgent(uint256 id, address wallet, uint256 pricePerJob) external onlyOwner {
        require(wallet != address(0), "zero wallet");
        Agent storage a = agents[id];
        a.wallet = wallet;
        a.pricePerJob = pricePerJob;
        a.active = true;
        emit AgentRegistered(id, wallet, pricePerJob);
    }

    /// @notice Pay an agent. msg.value is forwarded to the agent's payout wallet.
    function payAgent(uint256 id, uint256 jobId) external payable {
        Agent storage a = agents[id];
        require(a.active, "inactive agent");
        require(msg.value > 0, "no value");
        (bool ok, ) = a.wallet.call{value: msg.value}("");
        require(ok, "transfer failed");
        emit Paid(id, msg.sender, a.wallet, msg.value, jobId);
    }

    /// @notice Rate a completed job (score 1..5). Updates on-chain reputation.
    function rateJob(uint256 id, uint256 jobId, uint8 score) external onlyOwner {
        require(score >= 1 && score <= 5, "score 1..5");
        Agent storage a = agents[id];
        require(a.active, "inactive agent");
        a.ratingSum += score;
        a.jobs += 1;
        emit ReputationUpdated(id, _avgX100(a), a.jobs);
    }

    /// @return avgX100 average rating * 100 (e.g. 460 == 4.60), 0 if no jobs
    /// @return jobs number of rated jobs
    function reputation(uint256 id) external view returns (uint256 avgX100, uint64 jobs) {
        Agent storage a = agents[id];
        return (_avgX100(a), a.jobs);
    }

    function getAgent(uint256 id)
        external
        view
        returns (address wallet, uint256 pricePerJob, uint64 ratingSum, uint64 jobs, bool active)
    {
        Agent storage a = agents[id];
        return (a.wallet, a.pricePerJob, a.ratingSum, a.jobs, a.active);
    }

    function _avgX100(Agent storage a) internal view returns (uint256) {
        if (a.jobs == 0) return 0;
        return (uint256(a.ratingSum) * 100) / a.jobs;
    }
}
