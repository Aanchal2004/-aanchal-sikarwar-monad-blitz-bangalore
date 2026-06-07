'use client';
import { useEffect, useRef, useState, useCallback } from 'react';
import { Play, RotateCcw, Copy, ExternalLink, ArrowUp, ArrowDown } from 'lucide-react';
import { connectWs, postTask, type WsEvent, type Candidate } from '@/lib/api';

// ---------- types ----------
type SubtaskStatus = 'pending' | 'hiring' | 'paid' | 'working' | 'rated' | 'done';

interface SubtaskState {
  idx: number;
  description: string;
  skill: string;
  status: SubtaskStatus;
  candidates: Candidate[];
  selected: { agent_id: number; name: string; price_mon: number; reputation: number; utility: number; reasoning: string } | null;
  payment: { amount_mon: number; tx_hash: string; block: number; status: string; explorer: string } | null;
  work: string | null;
  rating: { score: number; rep_before: number; rep_after: number; tx_hash: string; explorer: string } | null;
}

interface LogEntry { ts: string; msg: string; highlight?: boolean }
interface PayFeedEntry { ts: string; tx_hash: string; explorer: string; amount_mon: number; agent_name: string; rep_delta?: number; positive?: boolean }

const EXAMPLES = [
  'Research competitors of Swiggy and summarize key differentiators',
  'Analyze the EV scooter market opportunity in Bangalore',
  'Create a product brief for an AI coding assistant',
];

function fmt(s: string) { return s.slice(0, 6) + '…' + s.slice(-4); }
function now() { return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' }); }

// ---------- component ----------
export default function ConsolePage() {
  const [prompt, setPrompt] = useState('');
  const [runId, setRunId] = useState<number | null>(null);
  const [running, setRunning] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [subtasks, setSubtasks] = useState<SubtaskState[]>([]);
  const [activeIdx, setActiveIdx] = useState(0);
  const [log, setLog] = useState<LogEntry[]>([]);
  const [feed, setFeed] = useState<PayFeedEntry[]>([]);
  const [finalResult, setFinalResult] = useState('');
  const [error, setError] = useState('');
  const wsRef = useRef<WebSocket | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

  const addLog = useCallback((msg: string, highlight = false) =>
    setLog(l => [...l, { ts: now(), msg, highlight }]), []);

  const handleEvent = useCallback((ev: WsEvent) => {
    switch (ev.type) {
      case 'run_started':
        addLog('Task received and parsed'); break;
      case 'decomposed':
        setSubtasks(ev.subtasks.map(s => ({
          idx: s.idx, description: s.description, skill: s.skill,
          status: 'pending', candidates: [], selected: null, payment: null, work: null, rating: null,
        })));
        addLog(`Decomposed into ${ev.subtasks.length} subtasks`);
        break;
      case 'candidates_evaluated':
        setSubtasks(p => p.map(s => s.idx === ev.subtask_idx ? { ...s, candidates: ev.candidates } : s));
        addLog(`Fetched ${ev.candidates.length} candidate agents for subtask ${ev.subtask_idx + 1}`);
        setActiveIdx(ev.subtask_idx);
        break;
      case 'agent_selected':
        setSubtasks(p => p.map(s => s.idx === ev.subtask_idx
          ? { ...s, status: 'hiring', selected: { agent_id: ev.agent_id, name: ev.name, price_mon: ev.price_mon, reputation: ev.reputation, utility: ev.utility, reasoning: ev.reasoning } }
          : s));
        addLog(`Selected ${ev.name} (utility ${ev.utility.toFixed(3)})`, true);
        addLog(`Sending payment and locking on-chain…`);
        break;
      case 'payment_confirmed':
        setSubtasks(p => p.map(s => s.idx === ev.subtask_idx
          ? { ...s, status: 'paid', payment: { amount_mon: ev.amount_mon, tx_hash: ev.tx_hash, block: ev.block, status: ev.status, explorer: ev.explorer } }
          : s));
        if (ev.tx_hash) {
          addLog(`Payment confirmed. Tx: ${fmt(ev.tx_hash)}`);
          setFeed(f => [{ ts: now(), tx_hash: ev.tx_hash, explorer: ev.explorer, amount_mon: ev.amount_mon, agent_name: '' }, ...f]);
        }
        break;
      case 'work_received':
        setSubtasks(p => p.map(s => s.idx === ev.subtask_idx ? { ...s, status: 'working', work: ev.output } : s));
        addLog(`Result received from ${ev.name}`);
        break;
      case 'reputation_updated':
        setSubtasks(p => p.map(s => s.idx === ev.subtask_idx
          ? { ...s, status: 'rated', rating: { score: ev.score, rep_before: ev.reputation_before, rep_after: ev.reputation_after, tx_hash: ev.tx_hash, explorer: ev.explorer } }
          : s));
        addLog(`Updating reputation on-chain (${ev.reputation_before} → ${ev.reputation_after})`);
        const delta = +(ev.reputation_after - ev.reputation_before).toFixed(2);
        setFeed(f => f.map((e, i) => i === 0 ? { ...e, agent_name: ev.name, rep_delta: Math.abs(delta), positive: delta >= 0 } : e));
        break;
      case 'run_completed':
        setFinalResult(ev.final_result);
        setRunning(false);
        setCompleted(true);
        addLog('Run completed', true);
        break;
      case 'run_failed':
        setError(ev.error);
        setRunning(false);
        addLog(`Run failed: ${ev.error}`);
        break;
    }
  }, [addLog]);

  const startRun = async () => {
    if (!prompt.trim() || running) return;
    setSubtasks([]); setLog([]); setFeed([]); setFinalResult(''); setError(''); setCompleted(false); setActiveIdx(0);
    setRunning(true);
    try {
      const { run_id } = await postTask(prompt.trim());
      setRunId(run_id);
      if (wsRef.current) wsRef.current.close();
      wsRef.current = connectWs(run_id, handleEvent);
    } catch (e) {
      setError(String(e)); setRunning(false);
    }
  };

  const reset = () => {
    wsRef.current?.close();
    setPrompt(''); setRunId(null); setRunning(false); setCompleted(false);
    setSubtasks([]); setLog([]); setFeed([]); setFinalResult(''); setError('');
  };

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' });
  }, [log]);
  useEffect(() => () => { wsRef.current?.close(); }, []);

  const hasRun = subtasks.length > 0 || running || completed;
  const activeTask = subtasks[activeIdx];

  // ---------- empty state ----------
  if (!hasRun) return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-7rem)] px-4">
      <div className="w-full max-w-xl rounded-2xl border border-gray-200 bg-white p-10 shadow-sm text-center">
        <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-50">
          <svg className="h-7 w-7 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
        </div>
        <h1 className="mb-2 text-2xl font-semibold text-gray-900">Start a task</h1>
        <p className="mb-6 text-sm text-gray-500">
          Describe what you want to achieve.<br />Your agent workforce will plan, execute, and deliver results.
        </p>
        <div className="flex gap-2">
          <input
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            placeholder="Describe the task for your agent workforce…"
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && startRun()}
          />
          <button
            onClick={startRun}
            className="flex items-center gap-2 rounded-lg bg-indigo-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-800 disabled:opacity-60"
            disabled={!prompt.trim()}
          >
            <Play className="h-4 w-4" /> Run Workforce
          </button>
        </div>
        <div className="mt-5">
          <p className="mb-3 text-xs text-gray-400">Try an example</p>
          <div className="flex flex-wrap justify-center gap-2">
            {EXAMPLES.map(ex => (
              <button key={ex} onClick={() => setPrompt(ex)}
                className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-1.5 text-xs text-gray-600 hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700 transition-colors">
                {ex}
              </button>
            ))}
          </div>
        </div>
        <p className="mt-6 text-xs text-gray-400">
          <span className="dot-live mr-1" />3 agents ready · Autonomous agents available and verified on-chain.
        </p>
      </div>
    </div>
  );

  // ---------- live console ----------
  return (
    <div className="flex flex-col" style={{ height: 'calc(100vh - 7rem)' }}>
      {/* Task bar */}
      <div className="flex items-center gap-3 border-b border-gray-200 bg-white px-6 py-3">
        <span className="shrink-0 text-xs font-medium text-gray-500 uppercase tracking-wide">Current Task</span>
        <input
          className="flex-1 rounded-md border border-gray-200 bg-gray-50 px-3 py-1.5 text-sm outline-none focus:border-indigo-400"
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          readOnly={running}
        />
        {running ? (
          <span className="pill-green shrink-0"><span className="dot-live" /> Running</span>
        ) : completed ? (
          <span className="pill-blue shrink-0">Completed</span>
        ) : null}
        {runId && <span className="mono text-xs text-gray-400 shrink-0">Run #{runId}</span>}
        <button onClick={reset} className="shrink-0 rounded-md border border-gray-200 p-1.5 text-gray-400 hover:text-gray-700">
          <RotateCcw className="h-4 w-4" />
        </button>
        {!running && !completed && (
          <button onClick={startRun} disabled={!prompt.trim()}
            className="shrink-0 flex items-center gap-1.5 rounded-md bg-indigo-700 px-4 py-1.5 text-sm font-medium text-white hover:bg-indigo-800 disabled:opacity-60">
            <Play className="h-3.5 w-3.5" /> Run Task
          </button>
        )}
      </div>

      {/* 3-column body */}
      <div className="flex flex-1 overflow-hidden">

        {/* LEFT: Manager Reasoning */}
        <aside className="flex w-72 shrink-0 flex-col border-r border-gray-200 bg-white">
          <div className="flex items-center justify-between border-b border-gray-100 px-4 py-2.5">
            <span className="text-xs font-semibold text-gray-700 uppercase tracking-wide">Manager Reasoning</span>
            <span className="pill-green text-[10px]"><span className="dot-live" /> Live</span>
          </div>
          <div ref={logRef} className="flex-1 overflow-y-auto px-4 py-3 space-y-1.5">
            {log.map((l, i) => (
              <div key={i} className="flex gap-2.5">
                <span className="mono shrink-0 text-[10px] text-gray-400 pt-0.5">{l.ts}</span>
                <span className={`text-xs leading-relaxed ${l.highlight ? 'font-medium text-indigo-700' : 'text-gray-600'}`}>{l.msg}</span>
              </div>
            ))}
          </div>
        </aside>

        {/* CENTER: Workflow + Candidates + Result */}
        <div className="flex flex-1 flex-col overflow-hidden">

          {/* Pipeline */}
          <div className="border-b border-gray-100 px-6 py-4">
            <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-500">Task Workflow</h2>
            <div className="flex items-center gap-0">
              {subtasks.map((st, i) => {
                const done = st.status === 'rated' || st.status === 'done';
                const active = st.idx === activeIdx && !done;
                return (
                  <div key={st.idx} className="flex items-center">
                    <button onClick={() => setActiveIdx(st.idx)}
                      className={`flex flex-col items-center rounded-xl border px-4 py-2.5 text-center transition-colors cursor-pointer w-40 ${
                        active ? 'border-indigo-300 bg-indigo-50' : done ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-white'
                      }`}>
                      <div className={`mb-1 flex h-6 w-6 items-center justify-center rounded-full text-[11px] font-semibold ${
                        active ? 'bg-indigo-600 text-white' : done ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-600'
                      }`}>{i + 1}</div>
                      <span className="text-[11px] font-medium text-gray-700 leading-tight line-clamp-2">{st.description.slice(0, 40)}{st.description.length > 40 ? '…' : ''}</span>
                      <span className={`mt-1 text-[10px] ${done ? 'text-green-600' : active ? 'text-indigo-600' : 'text-gray-400'}`}>
                        {done ? '✓ Done' : active ? 'In Progress' : 'Pending'}
                      </span>
                    </button>
                    {i < subtasks.length - 1 && <div className="h-px w-6 bg-gray-200 shrink-0" />}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Candidate agents table */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            {activeTask && (
              <>
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-gray-800">
                    Subtask {activeIdx + 1}: {activeTask.description.slice(0, 60)}{activeTask.description.length > 60 ? '…' : ''} — Candidate Agents
                  </h3>
                  <span className="pill-gray">{activeTask.skill}</span>
                </div>
                {activeTask.candidates.length > 0 ? (
                  <div className="overflow-hidden rounded-lg border border-gray-200">
                    <table className="w-full text-sm">
                      <thead className="border-b border-gray-200 bg-gray-50">
                        <tr>
                          {['Agent', 'Skill', 'Reputation', 'Price (MON)', 'Utility Score', 'Selected'].map(h => (
                            <th key={h} className="px-4 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {activeTask.candidates.map(c => {
                          const chosen = activeTask.selected?.agent_id === c.agent_id;
                          return (
                            <tr key={c.agent_id} className={`transition-colors ${chosen ? 'bg-indigo-50 border-l-2 border-l-indigo-500' : 'bg-white hover:bg-gray-50'}`}>
                              <td className="px-4 py-2.5 font-medium text-gray-900">{c.name}</td>
                              <td className="px-4 py-2.5 text-gray-500">{activeTask.skill}</td>
                              <td className="px-4 py-2.5">
                                <span className="flex items-center gap-1 text-amber-500">
                                  {'★'.repeat(Math.round(c.reputation))}{'☆'.repeat(5 - Math.round(c.reputation))}
                                  <span className="text-gray-700 ml-1">{c.reputation.toFixed(2)}</span>
                                </span>
                              </td>
                              <td className="px-4 py-2.5 text-gray-700">{c.price_mon}</td>
                              <td className="px-4 py-2.5">
                                <span className={`font-semibold ${chosen ? 'text-indigo-700' : 'text-gray-700'}`}>{c.utility.toFixed(3)}</span>
                              </td>
                              <td className="px-4 py-2.5">
                                {chosen ? (
                                  <span className="flex h-5 w-5 items-center justify-center rounded bg-indigo-600 text-white text-xs">✓</span>
                                ) : (
                                  <span className="block h-5 w-5 rounded border border-gray-300" />
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                    {activeTask.selected && (
                      <div className="border-t border-indigo-100 bg-indigo-50 px-4 py-2.5 text-xs text-indigo-700">
                        <span className="font-medium">Manager reasoning:</span> {activeTask.selected.reasoning}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex h-24 items-center justify-center rounded-lg border border-dashed border-gray-200 text-sm text-gray-400">
                    {running ? 'Evaluating candidates…' : 'Awaiting candidates'}
                  </div>
                )}

                {/* Work output */}
                {activeTask.work && (
                  <div className="mt-4">
                    <h4 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-gray-500">Output</h4>
                    <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-xs text-gray-700 leading-relaxed whitespace-pre-wrap max-h-40 overflow-y-auto">
                      {activeTask.work}
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Final result */}
            {finalResult && (
              <div className="mt-4">
                <h4 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-gray-500">Final Result (Live)</h4>
                <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-xs text-gray-700 leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto">
                  {finalResult}
                </div>
              </div>
            )}

            {error && (
              <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-xs text-red-700">{error}</div>
            )}
          </div>
        </div>

        {/* RIGHT: Payments & Reputation */}
        <aside className="flex w-72 shrink-0 flex-col border-l border-gray-200 bg-white">
          <div className="flex items-center justify-between border-b border-gray-100 px-4 py-2.5">
            <span className="text-xs font-semibold text-gray-700 uppercase tracking-wide">Payments & Reputation</span>
            <span className="pill-green text-[10px]"><span className="dot-live" /> Live</span>
          </div>
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2">
            {feed.length === 0 && (
              <p className="text-center text-xs text-gray-400 mt-8">Payments will appear here…</p>
            )}
            {feed.map((f, i) => (
              <div key={i} className="rounded-lg border border-gray-100 bg-gray-50 p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] text-gray-400">{f.ts}</span>
                  {f.rep_delta != null && (
                    <span className={`flex items-center gap-0.5 text-[11px] font-semibold ${f.positive ? 'text-green-600' : 'text-red-500'}`}>
                      {f.positive ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                      {f.positive ? '+' : '-'}{f.rep_delta}
                    </span>
                  )}
                </div>
                {f.tx_hash && (
                  <div className="flex items-center gap-1">
                    <span className="mono text-[11px] text-indigo-600 flex-1 truncate">{fmt(f.tx_hash)}</span>
                    <button onClick={() => navigator.clipboard.writeText(f.tx_hash)} className="text-gray-400 hover:text-gray-600">
                      <Copy className="h-3 w-3" />
                    </button>
                    {f.explorer && (
                      <a href={f.explorer} target="_blank" rel="noreferrer" className="text-gray-400 hover:text-indigo-600">
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                )}
                <div className="flex items-center justify-between mt-1">
                  <span className="text-xs text-gray-500">{f.agent_name || '…'}</span>
                  <span className="text-xs font-semibold text-gray-800">{f.amount_mon} MON</span>
                </div>
                <span className="pill-green text-[10px] mt-1">Confirmed</span>
              </div>
            ))}
          </div>
          {runId && (
            <div className="border-t border-gray-100 px-4 py-2.5">
              <a href={`/runs/${runId}`} className="block text-center text-xs text-indigo-600 hover:underline">
                View full run receipt →
              </a>
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
