import type { Metadata } from 'next';
import './globals.css';
import { NavBar } from '@/components/NavBar';
import { StatusBar } from '@/components/StatusBar';

export const metadata: Metadata = {
  title: 'AgentMandi',
  description: 'Autonomous AI workforce on Monad',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col bg-white text-gray-900">
        <NavBar />
        <main className="flex-1">{children}</main>
        <StatusBar />
      </body>
    </html>
  );
}
