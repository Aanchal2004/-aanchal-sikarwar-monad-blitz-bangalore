import { ExternalLink } from 'lucide-react';
import { getRun, getAgents } from '@/lib/api';
import Markdown from '@/components/Markdown';
import RepChange from '@/components/RepChange';
import DecisionBadge from '@/components/DecisionBadge';
import Link from 'next/link';
import {
  agentDisplayName,
  capabilityLabel,
  formatMonadSettlement,
  sanitizeAgentText,
} from '@/lib/display';

export const revalidate = 0;

function TxLink({ hash, explorer }: { hash: string; explorer: string }) {
  if (!hash) return <span className="text-gray-400 text-xs">—</span>;
  return (
    <span className="flex items-center gap-1">
      <span className="mono text-xs text-indigo-600">{hash.slice(0, 10)}…{hash.slice(-4)}</span>
      <a href={explorer} target="_blank" rel="noreferrer" className="text-gray-400 hover:text-indigo-600">
        <ExternalLink className="h-3 w-3" />
      </a>
    </span>
  );
}

export default async function RunPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let data: Awaited<ReturnType<typeof getRun>> | null = null;
  let agents: Awaited<ReturnType<typeof getAgents>> = [];
  try {
    data = await getRun(Number(id));
    agents = await getAgents();
  } catch { /* offline */ }

  if (!data || data.error) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-12 text-center text-sm text-gray-500">
        Run #{id} not found. <Link href="/console" className="text-indigo-600 hover:underline">Start a new run</Link>
      </div>
    );
  }

  const { run, subtasks, decisions, payments, ratings, summary, events } = data;
  const agentMap = Object.fromEntries(agents.map(a => [a.agent_id, a]));
  const decisionMap = Object.fromEntries((decisions ?? []).map((d: { subtask_id: number; [k: string]: unknown }) => [d.subtask_id, d]));
  const paymentMap = Object.fromEntries((payments ?? []).map((p: { subtask_id: number; [k: string]: unknown }) => [p.subtask_id, p]));
  const ratingMap = Object.fromEntries((ratings ?? []).map((r: { subtask_id: number; [k: string]: unknown }) => [r.subtask_id, r]));

  // Reputation before/after from event history
  const repEventMap: Record<number, { before: number; after: number; name: string; agent_id: number }> = {};
  for (const ev of events ?? []) {
    if (ev.type === 'reputation_updated' && ev.subtask_idx != null) {
      const st = subtasks.find((s: { idx: number; id: number }) => s.idx === ev.subtask_idx);
      if (st) {
        repEventMap[st.id] = {
          before: ev.reputation_before,
          after: ev.reputation_after,
          name: ev.name,
          agent_id: ev.agent_id,
        };
      }
    }
  }

  const hiringChanges = summary?.hiring_changes_rep ?? 0;

  return (
    <div className="mx-auto max-w-3xl px-6 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Run Summary</h1>
          <div className="mt-1 flex items-center gap-3 text-sm text-gray-500">
            <span className={run.status === 'completed' ? 'pill-green' : run.status === 'failed' ? 'pill-amber' : 'pill-blue'}>
              {run.status}
            </span>
            <span>Run #{run.id}</span>
            <span>{new Date(run.created_at).toLocaleString()}</span>
            <span>Network: Monad Testnet</span>
          </div>
        </div>
      </div>

      {/* Executive summary */}
      {summary && (
        <div className="mb-6 rounded-xl border border-indigo-200 bg-indigo-50 p-5">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-indigo-900">
              {run.status === 'completed' ? 'Goal Completed ✓' : 'Run In Progress'}
            </h2>
            {run.status === 'completed' && (
              <span className="rounded-full border border-amber-200 bg-amber-50 px-2.5 py-0.5 text-xs font-medium text-amber-700">
                Awaiting Human Review
              </span>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <div>
              <p className="text-[11px] font-medium uppercase tracking-wide text-indigo-500">Budget</p>
              <p className="text-lg font-bold text-indigo-900">{Number(summary.budget_mon ?? 0).toFixed(2)} MON</p>
            </div>
            <div>
              <p className="text-[11px] font-medium uppercase tracking-wide text-indigo-500">Spent</p>
              <p className="text-lg font-bold text-indigo-900">{Number(summary.total_spent_mon).toFixed(2)} MON</p>
            </div>
            <div>
              <p className="text-[11px] font-medium uppercase tracking-wide text-indigo-500">Savings</p>
              <p className="text-lg font-bold text-green-700">{Number(summary.cost_saved_pct ?? 0).toFixed(0)}%</p>
            </div>
            <div>
              <p className="text-[11px] font-medium uppercase tracking-wide text-indigo-500">Agents Hired</p>
              <p className="text-lg font-bold text-indigo-900">{summary.agents_hired ?? 0}</p>
            </div>
            <div className="sm:col-span-2">
              <p className="text-[11px] font-medium uppercase tracking-wide text-purple-600">Hiring Changes Due To Reputation</p>
              <p className={`text-lg font-bold ${hiringChanges > 0 ? 'text-purple-700' : 'text-indigo-900'}`}>{hiringChanges}</p>
            </div>
          </div>
        </div>
      )}

      {/* Workforce KPI strip */}
      {summary && (
        <div className="mb-6 flex flex-wrap items-center gap-x-6 gap-y-2 rounded-lg border border-gray-200 bg-white px-4 py-3">
          <span className="text-[11px] font-semibold uppercase tracking-wide text-gray-400">Workforce KPIs</span>
          <span className="text-xs text-gray-600">Agents Hired: <strong>{summary.agents_hired}</strong></span>
          <span className="text-xs text-gray-600">Payments Settled: <strong>{summary.confirmed ?? summary.payments}</strong></span>
          <span className="text-xs text-gray-600">Budget Used: <strong>{Number(summary.budget_utilization_pct ?? 0).toFixed(0)}%</strong></span>
          <span className={`text-xs ${hiringChanges > 0 ? 'font-semibold text-purple-700' : 'text-gray-600'}`}>
            Hiring Changes Due To Reputation: <strong>{hiringChanges}</strong>
          </span>
        </div>
      )}

      {/* Human Oversight */}
      <div className="mb-8 rounded-xl border border-gray-200 bg-white p-5">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">Human Oversight</h2>
        </div>
        <p className="mb-4 text-sm font-medium text-gray-700">
          Humans define goals and budgets. AgentMandi manages execution.
        </p>
        <div className="mb-4">
          <p className="text-[11px] font-medium uppercase tracking-wide text-gray-400">Original Goal</p>
          <p className="mt-0.5 text-sm text-gray-800">{run.prompt}</p>
        </div>
        <div className="grid grid-cols-2 gap-x-6 gap-y-3 sm:grid-cols-4">
          {[
            { label: 'Budget Provided', value: `${Number(run.budget_mon ?? summary?.budget_mon ?? 0).toFixed(2)} MON` },
            { label: 'Agents Hired', value: summary?.agents_hired ?? 0 },
            { label: 'Payments Executed', value: summary?.confirmed ?? summary?.payments ?? 0 },
            { label: 'Reputation Changes', value: (ratings ?? []).length },
          ].map(({ label, value }) => (
            <div key={label}>
              <p className="text-[11px] font-medium uppercase tracking-wide text-gray-400">{label}</p>
              <p className="mt-0.5 text-sm font-semibold text-gray-900">{value}</p>
            </div>
          ))}
        </div>
        <div className="mt-4 border-t border-gray-100 pt-3 text-xs text-gray-500">
          AgentMandi coordinated and paid the workforce autonomously. The final deliverable is
          {run.final_result ? ' ready for your review below.' : ' pending.'}
        </div>
      </div>

      {/* Timeline */}
      <div className="space-y-4 mb-8">
        {subtasks.map((st: { id: number; idx: number; description: string; skill: string; status: string }, i: number) => {
          const dec = decisionMap[st.id] as { selected_agent_id: number; utility: number; reasoning: string; candidates: unknown[] } | undefined;
          const pay = paymentMap[st.id] as { amount_mon: number; tx_hash: string; block: number; status: string; explorer: string; agent_id: number; latency_ms?: number } | undefined;
          const rate = ratingMap[st.id] as { score: number; tx_hash: string; agent_id: number } | undefined;
          const repEv = repEventMap[st.id];
          const agent = pay ? agentMap[pay.agent_id] : (dec ? agentMap[dec.selected_agent_id] : undefined);
          const displayName = agent ? agentDisplayName(agent.name, agent.agent_id) : (repEv ? agentDisplayName(repEv.name, repEv.agent_id) : 'Provider');

          if (st.status === 'skipped') {
            return (
              <div key={st.id} className="flex gap-4 opacity-70">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-300 text-sm font-semibold text-gray-600 shrink-0">{i + 1}</div>
                <div className="flex-1 pb-4">
                  <h3 className="font-semibold text-gray-500 mb-1">{st.description}</h3>
                  <span className="pill-gray text-xs">Skipped — over budget</span>
                </div>
              </div>
            );
          }

          return (
            <div key={st.id} className="flex gap-4">
              <div className="flex flex-col items-center">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-sm font-semibold text-white shrink-0">{i + 1}</div>
                {i < subtasks.length - 1 && <div className="flex-1 w-px bg-gray-200 my-1" />}
              </div>
              <div className="flex-1 pb-4">
                <div className="mb-2 flex items-start justify-between gap-2">
                  <h3 className="font-semibold text-gray-900">{st.description}</h3>
                  <span className="pill-gray shrink-0">{capabilityLabel(st.skill, agent?.agent_id)}</span>
                </div>
                <div className="rounded-xl border border-gray-200 divide-y divide-gray-100 overflow-hidden">
                  {dec && dec.selected_agent_id > 0 && (
                    <div className="flex items-start gap-4 px-4 py-3 bg-white">
                      <span className="shrink-0 text-xs font-medium text-gray-400 uppercase pt-0.5 w-20">Hiring</span>
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-gray-900">{displayName}</p>
                        <div className="mt-1 flex items-center gap-2">
                          <DecisionBadge reasoning={dec.reasoning} />
                        </div>
                        <p className="mt-1.5 text-xs text-gray-600">{sanitizeAgentText(dec.reasoning)}</p>
                      </div>
                    </div>
                  )}
                  {pay && (
                    <div className="flex items-center gap-4 px-4 py-3 bg-white">
                      <span className="shrink-0 text-xs font-medium text-gray-400 uppercase w-20">Payment</span>
                      <div className="flex-1 text-xs text-gray-700">
                        <span className="font-semibold">{displayName}</span> — Paid {pay.amount_mon} MON
                      </div>
                      <TxLink hash={pay.tx_hash} explorer={pay.explorer} />
                      <span className="pill-green text-[10px] shrink-0">{formatMonadSettlement(pay.latency_ms)}</span>
                    </div>
                  )}
                  {rate && repEv && (
                    <div className="flex items-center gap-4 px-4 py-3 bg-white">
                      <span className="shrink-0 text-xs font-medium text-gray-400 uppercase w-20">Reputation</span>
                      <div className="flex-1">
                        <RepChange before={repEv.before} after={repEv.after} />
                        <p className="mt-0.5 text-[11px] text-gray-500">Rating {rate.score}/5 — affects future hiring</p>
                      </div>
                    </div>
                  )}
                  {rate && !repEv && (
                    <div className="flex items-center gap-4 px-4 py-3 bg-white">
                      <span className="shrink-0 text-xs font-medium text-gray-400 uppercase w-20">Reputation</span>
                      <span className="text-xs text-gray-700">Rating: {rate.score}/5</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Headline impact: cost saved + Monad settlement */}
      {summary && (
        <div className="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-green-200 bg-green-50 p-5">
            <p className="text-3xl font-bold text-green-700">{Number(summary.cost_saved_pct ?? 0).toFixed(0)}% saved</p>
            <p className="mt-1 text-xs text-green-800">
              vs hiring the top-priced qualified provider every time
              ({Number(summary.premium_cost_mon ?? 0).toFixed(2)} MON → {Number(summary.total_spent_mon ?? 0).toFixed(2)} MON)
            </p>
          </div>
          <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-5">
            <p className="text-3xl font-bold text-indigo-700">
              {summary.settlements ?? 0} settlements
              {summary.avg_confirmation_ms ? ` · ${(Number(summary.avg_confirmation_ms) / 1000).toFixed(2)}s avg` : ''}
            </p>
            <p className="mt-1 text-xs text-indigo-800">
              Settled on Monad. Near-instant, sub-cent settlement makes per-subtask micropayments practical.
            </p>
          </div>
        </div>
      )}

      {/* Summary footer */}
      {summary && (
        <div className="grid grid-cols-3 gap-4 rounded-xl border border-gray-200 bg-gray-50 p-6 sm:grid-cols-6">
          {[
            { label: 'Budget', value: `${Number(summary.budget_mon ?? 0).toFixed(2)} MON` },
            { label: 'Total Spend', value: `${Number(summary.total_spent_mon).toFixed(3)} MON` },
            { label: 'Remaining', value: `${Number(summary.remaining_mon ?? 0).toFixed(3)} MON` },
            { label: 'Budget Used', value: `${Number(summary.budget_utilization_pct ?? 0).toFixed(0)}%` },
            { label: 'Avg / Subtask', value: `${Number(summary.avg_cost_per_subtask ?? 0).toFixed(3)} MON` },
            { label: 'Agents Hired', value: summary.agents_hired },
          ].map(({ label, value }) => (
            <div key={label} className="text-center">
              <p className="text-xs text-gray-500 mb-1">{label}</p>
              <p className="text-lg font-bold text-gray-900">{value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Final result */}
      {run.final_result && (
        <div className="mt-6">
          <h3 className="mb-2 text-sm font-semibold text-gray-700">Final Result</h3>
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <Markdown>{run.final_result}</Markdown>
          </div>
        </div>
      )}

      <div className="mt-6">
        <Link href="/console" className="text-sm text-indigo-600 hover:underline">← Back to Console</Link>
      </div>
    </div>
  );
}
