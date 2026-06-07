"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import type { Agent } from "@/lib/agents";
import { ReputationBadge } from "./ReputationBadge";
import { cn } from "@/lib/utils";

interface AgentCardProps {
  agent: Agent;
  className?: string;
}

export function AgentCard({ agent, className }: AgentCardProps) {
  return (
    <Link
      href={`/agents/${agent.id}`}
      className={cn(
        "glass group block rounded-xl p-5 transition hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5",
        className
      )}
    >
      <div className="mb-3 flex items-start justify-between">
        <span className="text-3xl">{agent.avatar}</span>
        <ReputationBadge score={agent.reputation} />
      </div>
      <h3 className="mb-1 font-semibold group-hover:text-primary">{agent.name}</h3>
      <p className="mb-3 line-clamp-2 text-sm text-muted-foreground">{agent.description}</p>
      <div className="mb-3 flex flex-wrap gap-1">
        {agent.skills.slice(0, 3).map((skill) => (
          <span
            key={skill}
            className="rounded-md bg-secondary px-2 py-0.5 text-xs text-muted-foreground"
          >
            {skill}
          </span>
        ))}
      </div>
      <div className="flex items-center justify-between text-sm">
        <span className="text-primary">{agent.pricePerTask}</span>
        <span className="flex items-center gap-1 text-muted-foreground group-hover:text-primary">
          View <ArrowRight className="h-4 w-4" />
        </span>
      </div>
    </Link>
  );
}
