import Link from "next/link";
import { notFound } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import { ReputationBadge } from "@/components/ReputationBadge";
import { WalletCard } from "@/components/WalletCard";
import { ChatInterface } from "@/components/ChatInterface";
import { MOCK_AGENTS } from "@/lib/agents";
import { ArrowLeft } from "lucide-react";

interface Props {
  params: Promise<{ id: string }>;
}

export default async function AgentProfilePage({ params }: Props) {
  const { id } = await params;
  const agent = MOCK_AGENTS.find((a) => a.id === id);
  if (!agent) notFound();

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />
      <div className="flex-1 p-6 lg:p-8">
        <Link
          href="/marketplace"
          className="mb-6 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" /> Back to Marketplace
        </Link>

        <div className="mb-8 flex items-start gap-6">
          <span className="text-6xl">{agent.avatar}</span>
          <div>
            <div className="mb-2 flex items-center gap-3">
              <h1 className="text-3xl font-bold">{agent.name}</h1>
              <ReputationBadge score={agent.reputation} />
            </div>
            <p className="mb-3 text-muted-foreground">{agent.description}</p>
            <div className="flex flex-wrap gap-2">
              {agent.skills.map((s) => (
                <span key={s} className="rounded-md bg-secondary px-2 py-1 text-xs">
                  {s}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <h2 className="mb-4 font-semibold">Chat with Agent</h2>
            <ChatInterface agentId={agent.id} className="min-h-[400px]" />
          </div>
          <div className="space-y-4">
            {agent.walletAddress && (
              <WalletCard address={agent.walletAddress} balance="0.42" />
            )}
            <div className="glass rounded-xl p-4">
              <div className="text-sm text-muted-foreground">Price per task</div>
              <div className="text-xl font-bold text-primary">{agent.pricePerTask}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
