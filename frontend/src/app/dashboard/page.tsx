import { Sidebar } from "@/components/Sidebar";
import { WalletCard } from "@/components/WalletCard";
import { Activity, Bot, Zap, Database } from "lucide-react";
import { API_BASE } from "@/lib/utils";

async function getHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    return res.json();
  } catch {
    return { status: "offline", provider: "—", model: "—" };
  }
}

export default async function DashboardPage() {
  const health = await getHealth();

  const stats = [
    { label: "Active Agents", value: "4", icon: Bot },
    { label: "Workflows Run", value: "12", icon: Zap },
    { label: "RAG Queries", value: "28", icon: Database },
    { label: "API Status", value: health.status, icon: Activity },
  ];

  return (
    <div className="flex min-h-[calc(100vh-4rem)]">
      <Sidebar />
      <div className="flex-1 p-6 lg:p-8">
        <h1 className="mb-2 text-2xl font-bold">Dashboard</h1>
        <p className="mb-8 text-muted-foreground">
          LLM: {health.provider} / {health.model}
        </p>

        <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map(({ label, value, icon: Icon }) => (
            <div key={label} className="glass rounded-xl p-5">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm text-muted-foreground">{label}</span>
                <Icon className="h-4 w-4 text-primary" />
              </div>
              <div className="text-2xl font-bold capitalize">{value}</div>
            </div>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <WalletCard address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0" balance="1.25" />
          <div className="glass rounded-xl p-6">
            <h3 className="mb-4 font-semibold">Quick Actions</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>→ Run multi-agent workflow from Demo page</li>
              <li>→ Query RAG: POST /rag/query</li>
              <li>→ Browse agents in Marketplace</li>
              <li>→ Add API keys to .env for real LLM responses</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
