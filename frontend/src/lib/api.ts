export const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'http://localhost:8000';

export interface Agent {
  agent_id: number;
  name: string;
  skill: string;
  wallet: string;
  price_mon: number;
  reputation: number;
  jobs: number;
  persona: string;
  explorer: string;
}

export interface Candidate {
  agent_id: number;
  name: string;
  price_mon: number;
  reputation: number;
  utility: number;
}

export interface HealthInfo {
  chain_ready: boolean;
  contract: string | null;
  manager: string | null;
  balance_mon: number | null;
  llm_provider: string;
}

export type WsEvent =
  | { type: 'run_started'; run_id: number; prompt: string }
  | { type: 'decomposed'; run_id: number; subtasks: { idx: number; description: string; skill: string }[] }
  | { type: 'candidates_evaluated'; run_id: number; subtask_idx: number; skill: string; candidates: Candidate[] }
  | { type: 'agent_selected'; run_id: number; subtask_idx: number; agent_id: number; name: string; price_mon: number; reputation: number; utility: number; reasoning: string }
  | { type: 'payment_sent'; run_id: number; subtask_idx: number; agent_id: number; amount_mon: number }
  | { type: 'payment_confirmed'; run_id: number; subtask_idx: number; agent_id: number; amount_mon: number; tx_hash: string; block: number; status: string; explorer: string }
  | { type: 'work_received'; run_id: number; subtask_idx: number; agent_id: number; name: string; output: string }
  | { type: 'reputation_updated'; run_id: number; subtask_idx: number; agent_id: number; name: string; score: number; reputation_before: number; reputation_after: number; tx_hash: string; explorer: string }
  | { type: 'run_completed'; run_id: number; final_result: string }
  | { type: 'run_failed'; run_id: number; error: string }
  | { type: 'low_balance'; run_id: number; balance_mon: number };

export async function getHealth(): Promise<HealthInfo> {
  const r = await fetch(`${BACKEND}/health`);
  return r.json();
}

export async function getAgents(): Promise<Agent[]> {
  const r = await fetch(`${BACKEND}/agents`, { cache: 'no-store' });
  return r.json();
}

export async function postTask(prompt: string): Promise<{ run_id: number }> {
  const r = await fetch(`${BACKEND}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  return r.json();
}

export async function getRun(runId: number) {
  const r = await fetch(`${BACKEND}/runs/${runId}`, { cache: 'no-store' });
  return r.json();
}

export function connectWs(runId: number, onEvent: (e: WsEvent) => void): WebSocket {
  const wsBase = BACKEND.replace(/^http/, 'ws');
  const ws = new WebSocket(`${wsBase}/ws/runs/${runId}`);
  ws.onmessage = (msg) => {
    try { onEvent(JSON.parse(msg.data)); } catch { /* ignore parse errors */ }
  };
  return ws;
}
