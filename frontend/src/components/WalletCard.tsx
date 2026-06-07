"use client";

import { Wallet, Copy } from "lucide-react";
import { cn } from "@/lib/utils";

interface WalletCardProps {
  address: string;
  balance?: string;
  network?: string;
  className?: string;
}

export function WalletCard({
  address,
  balance = "0.00",
  network = "Monad Testnet",
  className,
}: WalletCardProps) {
  const short = `${address.slice(0, 6)}...${address.slice(-4)}`;

  return (
    <div className={cn("glass rounded-xl p-4", className)}>
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Wallet className="h-5 w-5 text-primary" />
          <span className="text-sm font-medium">Agent Wallet</span>
        </div>
        <span className="rounded-full bg-primary/20 px-2 py-0.5 text-xs text-primary">
          {network}
        </span>
      </div>
      <div className="mb-2 font-mono text-lg font-semibold">{balance} MON</div>
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>{short}</span>
        <button
          type="button"
          className="rounded p-1 hover:bg-secondary"
          onClick={() => navigator.clipboard.writeText(address)}
          aria-label="Copy address"
        >
          <Copy className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
