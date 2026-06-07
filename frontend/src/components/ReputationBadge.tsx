import { Star } from "lucide-react";
import { cn } from "@/lib/utils";

interface ReputationBadgeProps {
  score: number;
  className?: string;
}

export function ReputationBadge({ score, className }: ReputationBadgeProps) {
  const color =
    score >= 4.5 ? "text-emerald-400" : score >= 4.0 ? "text-yellow-400" : "text-orange-400";

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full bg-secondary px-2 py-0.5 text-xs font-medium",
        className
      )}
    >
      <Star className={cn("h-3 w-3 fill-current", color)} />
      <span className={color}>{score.toFixed(1)}</span>
    </span>
  );
}
