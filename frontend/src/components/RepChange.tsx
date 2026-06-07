import { ArrowDown, ArrowUp } from 'lucide-react';
import { formatRepDelta } from '@/lib/display';

export default function RepChange({ before, after, compact = false }: { before: number; after: number; compact?: boolean }) {
  const { text, delta, up } = formatRepDelta(before, after);
  if (compact) {
    return (
      <span className={`inline-flex items-center gap-0.5 font-medium ${up ? 'text-green-600' : 'text-red-500'}`}>
        {text}
        {up ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
        {delta.toFixed(2)}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 text-xs">
      <span className="font-medium text-gray-800">{text}</span>
      <span className={`inline-flex items-center gap-0.5 rounded-full px-1.5 py-0.5 text-[11px] font-semibold ${up ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'}`}>
        {up ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
        {up ? '+' : '−'}{delta.toFixed(2)}
      </span>
    </span>
  );
}
