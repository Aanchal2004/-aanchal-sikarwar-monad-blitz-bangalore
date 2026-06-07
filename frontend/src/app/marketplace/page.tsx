import { Sidebar } from "@/components/Sidebar";
import { AgentCard } from "@/components/AgentCard";
import { MOCK_AGENTS } from "@/lib/agents";

export default function MarketplacePage() {
  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />
      <div className="flex-1 p-6 lg:p-8">
        <h1 className="mb-2 text-2xl font-bold">Agent Marketplace</h1>
        <p className="mb-8 text-muted-foreground">
          Discover and hire specialized AI agents. Extend with on-chain payments on Monad.
        </p>
        <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
          {MOCK_AGENTS.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      </div>
    </div>
  );
}
