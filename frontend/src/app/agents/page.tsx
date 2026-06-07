import { ExternalLink } from 'lucide-react';
import { getAgents } from '@/lib/api';

export const revalidate = 0;

function RepBar({ rep }: { rep: number }) {
  const pct = Math.round((rep / 5) * 100);
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-24 overflow-hidden rounded-full bg-gray-200">
        <div className="h-full rounded-full bg-indigo-600 transition-all" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-700">{rep.toFixed(2)}</span>
    </div>
  );
}

export default async function AgentsPage() {
  let agents: Awaited<ReturnType<typeof getAgents>> = [];
  try { agents = await getAgents(); } catch { /* backend offline */ }

  return (
    <div className="mx-auto max-w-screen-xl px-6 py-8">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
            Agent Registry <span className="rounded-full bg-gray-100 px-2.5 py-0.5 text-sm font-medium text-gray-600">{agents.length}</span>
          </h1>
          <p className="mt-1 text-sm text-gray-500">Browse and manage the autonomous workforce.</p>
        </div>
      </div>

      {agents.length === 0 ? (
        <div className="flex h-48 items-center justify-center rounded-xl border border-dashed border-gray-200 text-sm text-gray-400">
          No agents found. Make sure the backend is running.
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-gray-200">
          <table className="w-full text-sm">
            <thead className="border-b border-gray-200 bg-gray-50">
              <tr>
                {['Agent', 'Skill', 'Wallet', 'Price (MON)', 'Reputation', 'Jobs', 'Status', 'Explorer'].map(h => (
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
                        {a.name[0]}
                      </div>
                      <span className="font-medium text-gray-900">{a.name}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded-full border border-indigo-200 bg-indigo-50 px-2 py-0.5 text-xs text-indigo-700 capitalize">{a.skill}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="mono text-xs text-gray-500">{a.wallet.slice(0, 8)}…{a.wallet.slice(-4)}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-700">{a.price_mon}</td>
                  <td className="px-4 py-3"><RepBar rep={a.reputation} /></td>
                  <td className="px-4 py-3 text-gray-700">{a.jobs}</td>
                  <td className="px-4 py-3">
                    <span className={a.jobs > 0 ? 'pill-green' : 'pill-gray'}>{a.jobs > 0 ? 'Active' : 'Idle'}</span>
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
    </div>
  );
}
