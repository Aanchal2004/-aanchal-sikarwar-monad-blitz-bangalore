'use client';

import { useEffect, useRef, useState } from 'react';
import { ExternalLink, Plus, X } from 'lucide-react';
import { getAgents, registerAgent, type Agent, type AgentIn } from '@/lib/api';
import { agentDisplayName, agentTagline, capabilityLabel, SKILL_CAPABILITIES } from '@/lib/display';

const CAPABILITIES = Object.entries(SKILL_CAPABILITIES).map(([value, label]) => ({ value, label }));

function RepBar({ rep }: { rep: number }) {
  const pct = Math.round((rep / 5) * 100);
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-24 overflow-hidden rounded-full bg-gray-200">
        <div className="h-full rounded-full bg-indigo-600 transition-all" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-medium text-gray-800">{rep.toFixed(2)}</span>
    </div>
  );
}

const EMPTY_FORM: AgentIn = { name: '', skill: 'research', price_mon: 0.05, persona: '', operator: '' };

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<AgentIn>(EMPTY_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const nameRef = useRef<HTMLInputElement>(null);

  async function loadAgents() {
    try {
      setAgents(await getAgents());
    } catch {
      /* backend offline */
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadAgents(); }, []);
  useEffect(() => {
    if (showModal) setTimeout(() => nameRef.current?.focus(), 50);
  }, [showModal]);

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) { setError('Name is required'); return; }
    if (form.price_mon <= 0) { setError('Price must be > 0'); return; }
    setSubmitting(true);
    setError('');
    try {
      const newAgent = await registerAgent(form);
      setAgents(prev => [...prev, newAgent]);
      setShowModal(false);
      setForm(EMPTY_FORM);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-screen-xl px-6 py-8">
      {/* Header */}
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
            Agent Registry
            <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-sm font-medium text-gray-600">
              {agents.length}
            </span>
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Service providers in the AgentMandi workforce — each with its own wallet, capability, and on-chain reputation.
          </p>
        </div>
        <button
          onClick={() => { setShowModal(true); setError(''); }}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Register Agent
        </button>
      </div>

      {/* Table */}
      {loading ? (
        <div className="flex h-48 items-center justify-center text-sm text-gray-400">Loading…</div>
      ) : agents.length === 0 ? (
        <div className="flex h-48 items-center justify-center rounded-xl border border-dashed border-gray-200 text-sm text-gray-400">
          No agents found. Make sure the backend is running.
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-gray-200">
          <table className="w-full text-sm">
            <thead className="border-b border-gray-200 bg-gray-50">
              <tr>
                {['Provider', 'Operator', 'Capability', 'Price (MON)', 'Reputation', 'Jobs Completed', 'Status', 'Explorer'].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {agents.map(a => (
                <tr key={a.agent_id} className="bg-white hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2.5">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
                        {agentDisplayName(a.name, a.agent_id)[0]}
                      </div>
                      <div>
                        <span className="font-medium text-gray-900">{agentDisplayName(a.name, a.agent_id)}</span>
                        <p className="text-[11px] text-gray-500 mt-0.5 max-w-xs">{agentTagline(a.name, a.persona, a.agent_id)}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs text-gray-600">{a.operator || 'Independent'}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded-full border border-indigo-200 bg-indigo-50 px-2 py-0.5 text-xs text-indigo-700">
                      {capabilityLabel(a.skill, a.agent_id)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-700">{a.price_mon}</td>
                  <td className="px-4 py-3"><RepBar rep={a.reputation} /></td>
                  <td className="px-4 py-3 text-gray-700">{a.jobs}</td>
                  <td className="px-4 py-3">
                    {a.jobs > 0
                      ? <span className="pill-green">Active</span>
                      : <span className="rounded-full border border-blue-200 bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-700">New</span>
                    }
                  </td>
                  <td className="px-4 py-3">
                    <a href={a.explorer} target="_blank" rel="noreferrer"
                      className="flex items-center gap-1 text-xs text-indigo-600 hover:underline">
                      View <ExternalLink className="h-3 w-3" />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Register Agent Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl bg-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4">
              <h2 className="text-base font-semibold text-gray-900">Register New Provider</h2>
              <button onClick={() => setShowModal(false)} className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleRegister} className="px-6 py-5 space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Provider Name <span className="text-red-500">*</span></label>
                <input
                  ref={nameRef}
                  value={form.name}
                  onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                  placeholder="e.g. QuickResearch AI"
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-400"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Operator <span className="text-gray-400">(who runs this provider)</span></label>
                <input
                  value={form.operator}
                  onChange={e => setForm(f => ({ ...f, operator: e.target.value }))}
                  placeholder="e.g. Team Alpha, Acme Labs"
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-400"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Capability <span className="text-red-500">*</span></label>
                  <select
                    value={form.skill}
                    onChange={e => setForm(f => ({ ...f, skill: e.target.value }))}
                    className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-400"
                  >
                    {CAPABILITIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Price (MON) <span className="text-red-500">*</span></label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    value={form.price_mon}
                    onChange={e => setForm(f => ({ ...f, price_mon: parseFloat(e.target.value) || 0 }))}
                    className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Capability Description <span className="text-gray-400">(optional)</span></label>
                <textarea
                  value={form.persona}
                  onChange={e => setForm(f => ({ ...f, persona: e.target.value }))}
                  placeholder="One-line description of what this provider does…"
                  rows={2}
                  className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-400 resize-none"
                />
              </div>

              {error && (
                <p className="rounded-lg bg-red-50 border border-red-100 px-3 py-2 text-xs text-red-700">{error}</p>
              )}

              <div className="flex gap-3 pt-1">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-60 transition-colors"
                >
                  {submitting ? 'Registering on-chain…' : 'Register Provider'}
                </button>
              </div>

              {submitting && (
                <p className="text-center text-xs text-gray-400">
                  Generating wallet + submitting transaction to Monad testnet…
                </p>
              )}
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
