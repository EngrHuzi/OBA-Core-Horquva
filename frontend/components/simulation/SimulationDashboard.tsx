'use client';

import { useState, useMemo } from 'react';
import { Agent, Dependency } from '../../types';
import { rankScenarios, ScenarioResult } from '../../lib/simulation';
import { calculateHealthScore } from '../../lib/risk';
import { ScenarioRanking } from './ScenarioRanking';
import { ImpactSummary } from './ImpactSummary';
import { Activity, Beaker } from 'lucide-react';

interface SimulationDashboardProps {
  agents: Agent[];
  dependencies: Dependency[];
}

export function SimulationDashboard({ agents, dependencies }: SimulationDashboardProps) {
  const [activeScenarioId, setActiveScenarioId] = useState<string | null>(null);

  const baselineHealthScore = useMemo(() => calculateHealthScore(agents), [agents]);
  
  const scenarios = useMemo(() => rankScenarios(agents, dependencies), [agents, dependencies]);
  
  const activeScenario = useMemo(() => 
    scenarios.find(s => s.id === activeScenarioId) || null
  , [scenarios, activeScenarioId]);

  return (
    <div className="flex flex-col h-full space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center">
            What-If Simulation Engine
          </h1>
          <p className="text-slate-400 mt-1">
            Simulate personnel departures and agent failures to test organizational resilience.
          </p>
        </div>
        <div className="flex items-center space-x-3 bg-[#16161c] border border-slate-800 px-4 py-2 rounded-lg">
          <Activity className="w-5 h-5 text-emerald-400" />
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-500 uppercase tracking-wider font-semibold">Baseline Health</span>
            <span className="text-xl font-bold text-white leading-none">{baselineHealthScore} <span className="text-sm font-normal text-slate-500">/ 100</span></span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        {/* Left Column: Ranking List */}
        <div className="lg:col-span-1 overflow-hidden">
          <ScenarioRanking 
            scenarios={scenarios} 
            activeScenarioId={activeScenarioId} 
            onSelectScenario={(s) => setActiveScenarioId(s.id)} 
          />
        </div>

        {/* Right Column: Simulation Results */}
        <div className="lg:col-span-2 overflow-y-auto pr-2 pb-6">
          {activeScenario ? (
            <ImpactSummary scenario={activeScenario} />
          ) : (
            <div className="h-full flex flex-col items-center justify-center p-12 text-center border border-dashed border-slate-800 rounded-2xl bg-[#16161c]/50">
              <div className="w-16 h-16 rounded-full bg-purple-500/10 flex items-center justify-center mb-4 border border-purple-500/20">
                <Beaker className="w-8 h-8 text-purple-400" />
              </div>
              <h3 className="text-xl font-medium text-white mb-2">Ready for Simulation</h3>
              <p className="text-slate-400 max-w-md">
                Select a scenario from the ranking list on the left to see the estimated impact on the Organizational Health Score and identify cascade victims.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
