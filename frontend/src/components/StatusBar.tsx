'use client';
import { useEffect, useState } from 'react';
import { getHealth, type HealthInfo } from '@/lib/api';

export function StatusBar() {
  const [h, setH] = useState<HealthInfo | null>(null);

  useEffect(() => {
    getHealth().then(setH).catch(() => {});
    const id = setInterval(() => getHealth().then(setH).catch(() => {}), 10000);
    return () => clearInterval(id);
  }, []);

  return (
    <footer className="sticky bottom-0 z-40 border-t border-gray-200 bg-gray-50 px-6 py-1.5">
      <div className="mx-auto flex max-w-screen-2xl items-center gap-6 text-xs text-gray-500">
        <span className="flex items-center gap-1.5">
          <span className={`dot-live ${h?.chain_ready ? 'bg-green-500' : 'bg-amber-400'}`} />
          {h?.chain_ready ? 'Connected' : 'Connecting…'}
        </span>
        <span>Network: Monad Testnet</span>
        {h?.balance_mon != null && (
          <span>Balance: {h.balance_mon.toFixed(3)} MON</span>
        )}
        {h?.contract && (
          <span className="mono">
            Contract:{' '}
            <a
              href={`https://testnet.monadexplorer.com/address/${h.contract}`}
              target="_blank"
              rel="noreferrer"
              className="text-indigo-600 hover:underline"
            >
              {h.contract.slice(0, 8)}…{h.contract.slice(-4)}
            </a>
          </span>
        )}
        <span className="ml-auto">LLM: {h?.llm_provider ?? '…'}</span>
      </div>
    </footer>
  );
}
