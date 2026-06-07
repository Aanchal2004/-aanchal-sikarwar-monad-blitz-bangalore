export interface Agent {
  id: string;
  name: string;
  description: string;
  category: string;
  reputation: number;
  pricePerTask: string;
  avatar: string;
  skills: string[];
  walletAddress?: string;
}

export const MOCK_AGENTS: Agent[] = [
  {
    id: "planner-001",
    name: "PlanMaster",
    description: "Decomposes complex goals into hackathon-ready action plans.",
    category: "Planning",
    reputation: 4.8,
    pricePerTask: "0.01 MON",
    avatar: "🧠",
    skills: ["Planning", "Decomposition", "Risk Analysis"],
    walletAddress: "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
  },
  {
    id: "researcher-002",
    name: "DocScout",
    description: "RAG-powered researcher for Monad docs and technical discovery.",
    category: "Research",
    reputation: 4.6,
    pricePerTask: "0.02 MON",
    avatar: "🔍",
    skills: ["RAG", "Web Search", "Summarization"],
  },
  {
    id: "wallet-003",
    name: "ChainPilot",
    description: "Autonomous wallet agent for Monad testnet transactions.",
    category: "Blockchain",
    reputation: 4.9,
    pricePerTask: "0.05 MON",
    avatar: "💰",
    skills: ["Wallet", "Transactions", "Smart Contracts"],
    walletAddress: "0x8ba1f109551bD432803012645Ac136ddd64DBA72",
  },
  {
    id: "critic-004",
    name: "QualityGuard",
    description: "Reviews agent outputs before execution with security checks.",
    category: "Quality",
    reputation: 4.7,
    pricePerTask: "0.015 MON",
    avatar: "✅",
    skills: ["Review", "Security", "Validation"],
  },
];
