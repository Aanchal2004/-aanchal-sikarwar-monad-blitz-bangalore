"use client";

import { useState } from "react";
import { Play, CheckCircle2, Circle } from "lucide-react";
import { API_BASE } from "@/lib/utils";
import { LoadingSpinner } from "./LoadingSpinner";
import { cn } from "@/lib/utils";

interface WorkflowStep {
  agent: string;
  output: string;
  duration_ms?: number;
}

export function DemoPanel() {
  const [query, setQuery] = useState(
    "Build an agent marketplace with on-chain reputation on Monad"
  );
  const [loading, setLoading] = useState(false);
  const [steps, setSteps] = useState<WorkflowStep[]>([]);
  const [finalOutput, setFinalOutput] = useState("");
  const [activeStep, setActiveStep] = useState(-1);

  async function runWorkflow() {
    setLoading(true);
    setSteps([]);
    setFinalOutput("");
    setActiveStep(0);

    try {
      const res = await fetch(`${API_BASE}/agent/workflow`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();

      for (let i = 0; i < (data.steps?.length || 0); i++) {
        setActiveStep(i);
        await new Promise((r) => setTimeout(r, 400));
        setSteps((prev) => [...prev, data.steps[i]]);
      }
      setFinalOutput(data.final_output || "");
      setActiveStep(data.steps?.length || 0);
    } catch {
      setFinalOutput("Backend unavailable. Run: make backend");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="glass rounded-xl p-6">
        <h3 className="mb-4 text-lg font-semibold">Multi-Agent Workflow Demo</h3>
        <p className="mb-4 text-sm text-muted-foreground">
          Planner → Researcher → Critic → Executor
        </p>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={3}
          className="mb-4 w-full rounded-lg border border-input bg-background px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-ring"
        />
        <button
          type="button"
          onClick={runWorkflow}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-medium text-primary-foreground transition hover:opacity-90 disabled:opacity-50"
        >
          {loading ? <LoadingSpinner size="sm" /> : <Play className="h-4 w-4" />}
          Run Workflow
        </button>
      </div>

      {steps.length > 0 && (
        <div className="glass rounded-xl p-6">
          <h4 className="mb-4 font-medium">Pipeline Steps</h4>
          <div className="space-y-4">
            {["planner", "researcher", "critic", "executor"].map((name, i) => {
              const step = steps.find((s) => s.agent === name);
              const done = !!step;
              const current = activeStep === i && loading;

              return (
                <div key={name} className="flex gap-3">
                  {done ? (
                    <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-400" />
                  ) : current ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <Circle className="h-5 w-5 shrink-0 text-muted-foreground" />
                  )}
                  <div className="flex-1">
                    <div className="mb-1 flex items-center gap-2">
                      <span className="font-medium capitalize">{name}</span>
                      {step?.duration_ms != null && (
                        <span className="text-xs text-muted-foreground">
                          {step.duration_ms}ms
                        </span>
                      )}
                    </div>
                    {step && (
                      <p className="text-sm text-muted-foreground line-clamp-3">
                        {step.output}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {finalOutput && (
        <div className={cn("glass rounded-xl p-6 border border-primary/30")}>
          <h4 className="mb-2 font-medium text-primary">Final Output</h4>
          <p className="whitespace-pre-wrap text-sm">{finalOutput}</p>
        </div>
      )}
    </div>
  );
}
