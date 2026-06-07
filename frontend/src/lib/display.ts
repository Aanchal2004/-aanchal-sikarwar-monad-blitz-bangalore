/** Display-layer mappings: capability-oriented language for judges & operators. */

export const AGENT_PROFILES: Record<number, { capability: string; tagline: string; dataAccess?: string }> = {
  1: {
    capability: 'Market Sizing & D2C Landscape',
    tagline: 'India D2C & social-commerce market sizing, TAM/SAM, and key players',
    dataAccess: 'Public market reports, industry news, startup databases',
  },
  2: {
    capability: 'Competitive Positioning Intelligence',
    tagline: 'Competitive positioning vs Bikayi, Shopify, and social-commerce stacks',
    dataAccess: 'Competitor sites, product docs, pricing pages, G2/Capterra',
  },
  3: {
    capability: 'Executive Go/No-Go Briefs',
    tagline: 'One-page go/no-go executive briefs with risks and next steps',
    dataAccess: 'Prior subtask outputs + board-ready templates',
  },
  4: {
    capability: 'SaaS Stack Benchmarking',
    tagline: 'SaaS tool landscape scanning and feature benchmarking',
    dataAccess: 'Product comparison matrices, feature lists',
  },
};

export const SKILL_CAPABILITIES: Record<string, string> = {
  research: 'Market & Competitive Research',
  writing: 'Executive Go/No-Go Briefs',
  analysis: 'Data Analysis & Insights',
  coding: 'Software Development',
  data: 'Data Processing & ETL',
  marketing: 'Marketing & GTM Research',
  legal: 'Legal & Compliance Review',
};

const CANONICAL_NAMES: Record<number, string> = {
  1: 'MarketScope AI',
  2: 'CompEdge AI',
  3: 'BriefForge AI',
  4: 'StackLens AI',
};

/** Old names → current display names (reasoning text from prior runs). */
const LEGACY_TEXT_NAMES: Record<string, string> = {
  Asha: 'MarketScope AI',
  Bhavna: 'CompEdge AI',
  Chetan: 'BriefForge AI',
  Deepa: 'StackLens AI',
  'Deepa ': 'StackLens AI',
  'QuickResearch AI': 'MarketScope AI',
  'Alpha Insights AI': 'CompEdge AI',
  'ReportForge AI': 'BriefForge AI',
  'FormatPro AI': 'StackLens AI',
};

export function agentDisplayName(name: string, agentId?: number): string {
  if (agentId && CANONICAL_NAMES[agentId]) return CANONICAL_NAMES[agentId];
  const trimmed = name.trim();
  if (LEGACY_TEXT_NAMES[trimmed]) return LEGACY_TEXT_NAMES[trimmed];
  if (trimmed.endsWith(' AI')) return trimmed;
  return trimmed;
}

export function sanitizeAgentText(text: string): string {
  let out = text;
  for (const [old, display] of Object.entries(LEGACY_TEXT_NAMES)) {
    out = out.replaceAll(old.trim(), display);
  }
  return out;
}

export function capabilityLabel(skill: string, agentId?: number): string {
  if (agentId && AGENT_PROFILES[agentId]?.capability) return AGENT_PROFILES[agentId].capability;
  return SKILL_CAPABILITIES[skill] ?? skill.replace(/^\w/, c => c.toUpperCase());
}

export function agentTagline(_name: string, persona: string, agentId?: number): string {
  if (agentId && AGENT_PROFILES[agentId]?.tagline) return AGENT_PROFILES[agentId].tagline;
  if (persona?.trim()) return persona.trim();
  return capabilityLabel('', agentId);
}

export type DecisionLabel =
  | 'Best Value'
  | 'Highest Reputation'
  | 'Budget Optimized'
  | 'Reputation-Driven Change'
  | 'Premium Capability Required'
  | 'Cheapest Qualified Provider';

export function deriveDecisionLabel(reasoning: string, decisionLabel?: string): DecisionLabel {
  if (decisionLabel) return decisionLabel as DecisionLabel;
  const r = reasoning.toLowerCase();
  if (r.includes('remaining budget') || r.includes('cost efficiency')) return 'Budget Optimized';
  if (r.includes('previously hired') || r.includes('reputation fell') || r.includes('switching to')) return 'Reputation-Driven Change';
  if (r.includes('paying a premium') || r.includes('top reputation') || r.includes('quality wins')) return 'Highest Reputation';
  if (r.includes('best value')) return 'Best Value';
  if (r.includes('cheapest')) return 'Cheapest Qualified Provider';
  return 'Best Value';
}

export function isReputationDrivenChange(reasoning: string): boolean {
  return deriveDecisionLabel(reasoning) === 'Reputation-Driven Change';
}

export const DECISION_BADGE_STYLES: Record<DecisionLabel, string> = {
  'Best Value': 'border-green-200 bg-green-50 text-green-800',
  'Highest Reputation': 'border-amber-200 bg-amber-50 text-amber-800',
  'Budget Optimized': 'border-blue-200 bg-blue-50 text-blue-800',
  'Reputation-Driven Change': 'border-purple-200 bg-purple-50 text-purple-800',
  'Premium Capability Required': 'border-indigo-200 bg-indigo-50 text-indigo-800',
  'Cheapest Qualified Provider': 'border-gray-200 bg-gray-50 text-gray-700',
};

export function formatRepDelta(before: number, after: number): { text: string; delta: number; up: boolean } {
  const delta = +(after - before).toFixed(2);
  return { text: `${before.toFixed(2)} → ${after.toFixed(2)}`, delta: Math.abs(delta), up: delta >= 0 };
}

export function formatMonadSettlement(latencyMs?: number): string {
  if (!latencyMs) return 'Settled on Monad';
  return `Settled on Monad • Confirmed in ${(latencyMs / 1000).toFixed(1)}s`;
}
