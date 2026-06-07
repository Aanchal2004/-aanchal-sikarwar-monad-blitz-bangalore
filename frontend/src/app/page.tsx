import Link from "next/link";
import { ArrowRight, Bot, Layers, Zap, Shield } from "lucide-react";
import { AgentCard } from "@/components/AgentCard";
import { MOCK_AGENTS } from "@/lib/agents";

export default function LandingPage() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden px-4 py-24">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/10 via-transparent to-transparent" />
        <div className="relative mx-auto max-w-4xl text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-sm text-primary">
            <Zap className="h-4 w-4" />
            Monad Blitz Bangalore — Ship in 6 hours
          </div>
          <h1 className="mb-6 text-5xl font-bold tracking-tight md:text-6xl">
            Build <span className="gradient-text">AI Agents</span>
            <br />
            on Monad Blockchain
          </h1>
          <p className="mb-8 text-lg text-muted-foreground">
            Pre-built starter kit for multi-agent systems, RAG, agent wallets,
            marketplaces, and on-chain reputation. Demo-ready in one day.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/demo"
              className="flex items-center gap-2 rounded-lg bg-primary px-6 py-3 font-medium text-primary-foreground transition hover:opacity-90"
            >
              Run Demo Workflow <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/chat"
              className="rounded-lg border border-border px-6 py-3 font-medium transition hover:bg-secondary"
            >
              Open Chat
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-7xl px-4 py-16">
        <h2 className="mb-10 text-center text-2xl font-bold">Everything You Need</h2>
        <div className="grid gap-6 md:grid-cols-3">
          {[
            {
              icon: Bot,
              title: "Multi-Agent Framework",
              desc: "Planner → Researcher → Critic → Executor pipeline with LangGraph hooks",
            },
            {
              icon: Layers,
              title: "RAG Pipeline",
              desc: "Document loading, chunking, embeddings, retrieval — modular and swappable",
            },
            {
              icon: Shield,
              title: "Monad Integration",
              desc: "Wallet agents, transaction examples, and on-chain reputation patterns",
            },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="glass rounded-xl p-6">
              <Icon className="mb-4 h-8 w-8 text-primary" />
              <h3 className="mb-2 font-semibold">{title}</h3>
              <p className="text-sm text-muted-foreground">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Featured Agents */}
      <section className="mx-auto max-w-7xl px-4 py-16">
        <div className="mb-8 flex items-center justify-between">
          <h2 className="text-2xl font-bold">Featured Agents</h2>
          <Link href="/marketplace" className="text-sm text-primary hover:underline">
            View all →
          </Link>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {MOCK_AGENTS.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      </section>
    </div>
  );
}
