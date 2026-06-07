import { ExternalLink, Copy } from 'lucide-react';
import { getRun } from '@/lib/api';
import Link from 'next/link';

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
  try { data = await getRun(Number(id)); } catch { /* offline */ }

  if (!data || data.error) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-12 text-center text-sm text-gray-500">
        Run #{id} not found. <Link href="/console" className="text-indigo-600 hover:underline">Start a new run</Link>
      </div>
    );
  }

  const { run, subtasks, decisions, payments, ratings, summary } = data;
  const decisionMap = Object.fromEntries((decisions ?? []).map((d: { subtask_id: number; [k: string]: unknown }) => [d.subtask_id, d]));
  const paymentMap = Object.fromEntries((payments ?? []).map((p: { subtask_id: number; [k: string]: unknown }) => [p.subtask_id, p]));
  const ratingMap  = Object.fromEntries((ratings  ?? []).map((r: { subtask_id: number; [k: string]: unknown }) => [r.subtask_id, r]));

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

      {/* Timeline */}
      <div className="space-y-4 mb-8">
        {subtasks.map((st: { id: number; idx: number; description: string; skill: string; status: string }, i: number) => {
          const dec  = decisionMap[st.id] as { selected_agent_id: number; utility: number; reasoning: string; candidates: unknown[] } | undefined;
          const pay  = paymentMap[st.id] as { amount_mon: number; tx_hash: string; block: number; status: string; explorer: string } | undefined;
          const rate = ratingMap[st.id] as { score: number; tx_hash: string } | undefined;

          return (
            <div key={st.id} className="flex gap-4">
              <div className="flex flex-col items-center">
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-sm font-semibold text-white shrink-0">{i + 1}</div>
                {i < subtasks.length - 1 && <div className="flex-1 w-px bg-gray-200 my-1" />}
              </div>
              <div className="flex-1 pb-4">
                <h3 className="font-semibold text-gray-900 mb-2">{st.description}</h3>
                <div className="rounded-xl border border-gray-200 divide-y divide-gray-100 overflow-hidden">
                  {dec && (
                    <div className="flex items-start gap-4 px-4 py-3 bg-white">
                      <span className="shrink-0 text-xs font-medium text-gray-400 uppercase pt-0.5 w-20">Decision</span>
                      <div className="flex-1 text-xs text-gray-700">{dec.reasoning}</div>
                      <span className="shrink-0 text-xs font-semibold text-indigo-700">Utility: {Number(dec.utility).toFixed(3)}</span>
                    </div>
                  )}
                  {pay && (
                    <div className="flex items-center gap-4 px-4 py-3 bg-white">
                      <span className="shrink-0 text-xs font-medium text-gray-400 uppercase w-20">Payment</span>
                      <span className="text-xs text-gray-700 flex-1">Paid agent for task execution</span>
                      <span className="text-xs font-semibold text-gray-800">{pay.amount_mon} MON</span>
                      <TxLink hash={pay.tx_hash} explorer={pay.explorer} />
                      {pay.block > 0 && <span className="text-xs text-gray-400">Block: {pay.block.toLocaleString()}</span>}
                    </div>
                  )}
                  {rate && (
                    <div className="flex items-center gap-4 px-4 py-3 bg-white">
                      <span className="shrink-0 text-xs font-medium text-gray-400 uppercase w-20">Reputation</span>
                      <span className="text-xs text-gray-700 flex-1">Rating: {rate.score}/5</span>
                      <TxLink hash={rate.tx_hash} explorer={''} />
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary footer */}
      {summary && (
        <div className="grid grid-cols-4 gap-4 rounded-xl border border-gray-200 bg-gray-50 p-6">
          {[
            { label: 'Total Paid', value: `${Number(summary.total_spent_mon).toFixed(3)} MON` },
            { label: 'Payments', value: summary.payments },
            { label: 'Confirmed', value: summary.confirmed },
            { label: 'Agents Hired', value: summary.agents_hired },
          ].map(({ label, value }) => (
            <div key={label} className="text-center">
              <p className="text-xs text-gray-500 mb-1">{label}</p>
              <p className="text-xl font-bold text-gray-900">{value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Final result */}
      {run.final_result && (
        <div className="mt-6">
          <h3 className="mb-2 text-sm font-semibold text-gray-700">Final Result</h3>
          <div className="rounded-xl border border-gray-200 bg-gray-50 p-4 text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">
            {run.final_result}
          </div>
        </div>
      )}

      <div className="mt-6">
        <Link href="/console" className="text-sm text-indigo-600 hover:underline">← Back to Console</Link>
      </div>
    </div>
  );
}
