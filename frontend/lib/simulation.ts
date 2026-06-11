import { Agent, Dependency, RiskLevel } from '../types';
import { calculateHealthScore, deriveRisk, deriveRiskScore } from './risk';
import { getDownstream, getSPOFs } from './graph';

export interface SimulatedAgent extends Agent {
  _simulation_override?: number;
  _simulation_penalty?: number;
  _baseline_risk_level?: RiskLevel;
  _baseline_risk_score?: number;
}

export interface ScenarioResult {
  id: string;
  type: 'PERSON_LEAVES' | 'AGENT_FAILS';
  targetId: string;
  targetName: string;
  baselineHealthScore: number;
  simulatedHealthScore: number;
  healthScoreDelta: number;
  impactedAgents: {
    agentId: string;
    agentName: string;
    beforeRisk: RiskLevel;
    afterRisk: RiskLevel;
    reason: string;
  }[];
  simulatedAgents: SimulatedAgent[];
}

export function simulatePersonLeaving(
  personName: string,
  agents: Agent[],
  dependencies: Dependency[]
): ScenarioResult {
  const baselineHealthScore = calculateHealthScore(agents);
  
  const simulatedAgents: SimulatedAgent[] = agents.map(a => ({
    ...a,
    _baseline_risk_level: deriveRisk(a),
    _baseline_risk_score: deriveRiskScore(a)
  }));

  const impactedAgents: ScenarioResult['impactedAgents'] = [];

  simulatedAgents.forEach(agent => {
    let affected = false;
    let reason = '';

    if (agent.owner === personName) {
      agent._simulation_penalty = (agent._simulation_penalty || 0) + 35;
      affected = true;
      reason = 'Orphaned (+35 Risk)';
    }
    if (agent.backup_owner === personName) {
      // If we also want to add a penalty for losing backup, we could, 
      // but prompt only specifically requires +35 for becoming orphaned.
      affected = true;
      reason = reason ? 'Orphaned & Backup Lost' : 'Backup Lost';
    }

    if (affected) {
      const newRisk = deriveRisk(agent);
      impactedAgents.push({
        agentId: agent.id,
        agentName: agent.name,
        beforeRisk: agent._baseline_risk_level!,
        afterRisk: newRisk,
        reason
      });
    }
  });

  const simulatedHealthScore = calculateHealthScore(simulatedAgents);

  return {
    id: `person_leaves_${personName}`,
    type: 'PERSON_LEAVES',
    targetId: personName,
    targetName: personName,
    baselineHealthScore,
    simulatedHealthScore,
    healthScoreDelta: simulatedHealthScore - baselineHealthScore,
    impactedAgents,
    simulatedAgents,
  };
}

export function simulateAgentFailing(
  agentId: string,
  agents: Agent[],
  dependencies: Dependency[]
): ScenarioResult {
  const baselineHealthScore = calculateHealthScore(agents);
  const targetAgent = agents.find(a => a.id === agentId);
  
  const simulatedAgents: SimulatedAgent[] = agents.map(a => ({
    ...a,
    _baseline_risk_level: deriveRisk(a),
    _baseline_risk_score: deriveRiskScore(a)
  }));

  const impactedAgents: ScenarioResult['impactedAgents'] = [];
  const cascadeVictims = getDownstream(agentId, dependencies);

  simulatedAgents.forEach(agent => {
    if (agent.id === agentId) {
      agent._simulation_override = 170; // Max risk
      const newRisk = deriveRisk(agent);
      impactedAgents.push({
        agentId: agent.id,
        agentName: agent.name,
        beforeRisk: agent._baseline_risk_level!,
        afterRisk: newRisk,
        reason: 'Primary Failure'
      });
    } else if (cascadeVictims.has(agent.id)) {
      agent._simulation_penalty = 30;
      const newRisk = deriveRisk(agent);
      if (newRisk !== agent._baseline_risk_level) {
        impactedAgents.push({
          agentId: agent.id,
          agentName: agent.name,
          beforeRisk: agent._baseline_risk_level!,
          afterRisk: newRisk,
          reason: 'Cascade Victim (+30 Risk)'
        });
      }
    }
  });

  const simulatedHealthScore = calculateHealthScore(simulatedAgents);

  return {
    id: `agent_fails_${agentId}`,
    type: 'AGENT_FAILS',
    targetId: agentId,
    targetName: targetAgent ? targetAgent.name : agentId,
    baselineHealthScore,
    simulatedHealthScore,
    healthScoreDelta: simulatedHealthScore - baselineHealthScore,
    impactedAgents,
    simulatedAgents,
  };
}

export function rankScenarios(agents: Agent[], dependencies: Dependency[]): ScenarioResult[] {
  const scenarios: ScenarioResult[] = [];

  // Get unique owners and backups
  const people = new Set<string>();
  agents.forEach(a => {
    if (a.owner) people.add(a.owner);
    if (a.backup_owner) people.add(a.backup_owner);
  });

  // Run 'Person Leaves' scenarios
  people.forEach(person => {
    scenarios.push(simulatePersonLeaving(person, agents, dependencies));
  });

  // Run 'Agent Fails' scenarios for CRITICAL, HIGH, and SPOF agents
  const spofs = getSPOFs(agents, dependencies).map(s => s.agentId);
  agents.forEach(agent => {
    const riskLevel = deriveRisk(agent);
    if (riskLevel === 'critical' || riskLevel === 'high' || spofs.includes(agent.id)) {
      scenarios.push(simulateAgentFailing(agent.id, agents, dependencies));
    }
  });

  // Sort by worst impact (lowest simulated health score)
  scenarios.sort((a, b) => a.simulatedHealthScore - b.simulatedHealthScore);

  return scenarios;
}
