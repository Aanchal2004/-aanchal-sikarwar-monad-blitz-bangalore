'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Bot } from 'lucide-react';

const TABS = [
  { label: 'Operations Console', href: '/console' },
  { label: 'Agents', href: '/agents' },
  { label: 'Runs', href: '/runs' },
];

export function NavBar() {
  const path = usePathname();
  return (
    <header className="sticky top-0 z-40 border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-14 max-w-screen-2xl items-center gap-8 px-6">
        <Link href="/console" className="flex items-center gap-2 font-semibold text-indigo-700 shrink-0">
          <Bot className="h-5 w-5" />
          AgentMandi
        </Link>
        <nav className="flex items-end gap-0 h-full">
          {TABS.map((t) => {
            const active = path === t.href || (t.href !== '/console' && path.startsWith(t.href));
            return (
              <Link
                key={t.href}
                href={t.href}
                className={`relative flex h-full items-center px-4 text-sm transition-colors ${
                  active
                    ? 'text-indigo-700 font-medium after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-indigo-700'
                    : 'text-gray-500 hover:text-gray-900'
                }`}
              >
                {t.label}
              </Link>
            );
          })}
        </nav>
        <div className="ml-auto flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-xs text-gray-500">
            <span className="dot-live" />
            Monad Testnet
          </span>
          <span className="mono rounded border border-gray-200 bg-gray-50 px-2 py-1 text-xs text-gray-600">
            0xa95c…d358
          </span>
        </div>
      </div>
    </header>
  );
}
