import { deriveDecisionLabel, DECISION_BADGE_STYLES, type DecisionLabel } from '@/lib/display';

export default function DecisionBadge({ reasoning, label }: { reasoning?: string; label?: string }) {
  const resolved = (label ?? deriveDecisionLabel(reasoning ?? '')) as DecisionLabel;
  const style = DECISION_BADGE_STYLES[resolved] ?? DECISION_BADGE_STYLES['Best Value'];
  return (
    <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-semibold ${style}`}>
      ✓ {resolved}
    </span>
  );
}
