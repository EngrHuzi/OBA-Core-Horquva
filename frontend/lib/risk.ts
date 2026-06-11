import { Agent, RiskLevel } from '../types';

/**
 * Derives a governance-based Risk level from the agent's ownership,
 * documentation, and criticality — mirroring the OBA Core scoring logic:
 *   No owner        → +40
 *   No backup owner → +30
 *   Not documented  → +15
 *   Criticality     → critical +15 / high +10 / medium +5 / low +0
 *
 * Score → Risk tier:
 *   ≥ 70  → CRITICAL
 *   ≥ 40  → HIGH
 *   ≥ 20  → MEDIUM
 *   <  20 → LOW
 */
export function deriveRisk(agent: Agent): RiskLevel {
  let score = 0;
  if (!agent.owner)        score += 40;
  if (!agent.backup_owner) score += 30;
  if (!agent.documented)   score += 15;

  const critWeight: Record<RiskLevel, number> = {
    critical: 15,
    high: 10,
    medium: 5,
    low: 0,
  };
  score += critWeight[agent.criticality];

  if (score >= 70) return 'critical';
  if (score >= 40) return 'high';
  if (score >= 20) return 'medium';
  return 'low';
}
