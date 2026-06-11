import { AlertTriangle, UserMinus, ShieldOff } from 'lucide-react';
import { ScenarioResult } from '../../lib/simulation';

interface ScenarioRankingProps {
  scenarios: ScenarioResult[];
  activeScenarioId: string | null;
  onSelectScenario: (scenario: ScenarioResult) => void;
}

export function ScenarioRanking({ scenarios, activeScenarioId, onSelectScenario }: ScenarioRankingProps) {
  // Sort scenarios by worst impact (lowest simulated score)
  const rankedScenarios = [...scenarios].sort((a, b) => a.simulatedHealthScore - b.simulatedHealthScore);

  return (
    <div className="card p-6 h-full flex flex-col">
      <div className="mb-6">
        <h3 className="text-lg font-medium text-white flex items-center">
          <AlertTriangle className="w-5 h-5 text-red-400 mr-2" />
          Highest Risk Scenarios
        </h3>
        <p className="text-sm text-slate-400 mt-1">
          Ranked by maximum potential drop in Organizational Health Score
        </p>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 space-y-2">
        {rankedScenarios.map((scenario, index) => {
          const isActive = scenario.id === activeScenarioId;
          const drop = scenario.baselineHealthScore - scenario.simulatedHealthScore;
          
          return (
            <button
              key={scenario.id}
              onClick={() => onSelectScenario(scenario)}
              className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
                isActive 
                  ? 'bg-red-500/10 border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.1)]' 
                  : 'bg-[#1a1a24] border-slate-800/50 hover:border-slate-700 hover:bg-[#1f1f2a]'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  {scenario.type === 'PERSON_LEAVES' ? (
                    <UserMinus className={`w-4 h-4 ${isActive ? 'text-red-400' : 'text-slate-400'}`} />
                  ) : (
                    <ShieldOff className={`w-4 h-4 ${isActive ? 'text-orange-400' : 'text-slate-400'}`} />
                  )}
                  <span className={`text-sm font-medium ${isActive ? 'text-white' : 'text-slate-200'}`}>
                    If {scenario.targetName} {scenario.type === 'PERSON_LEAVES' ? 'leaves' : 'fails'}
                  </span>
                </div>
                {index === 0 && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider bg-red-500/20 text-red-400 border border-red-500/30">
                    #1 DANGER
                  </span>
                )}
              </div>
              
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500">
                  {scenario.impactedAgents.length} agents impacted
                </span>
                <span className={`font-semibold ${isActive ? 'text-red-400' : 'text-red-400/70'}`}>
                  -{drop} Health Score
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
