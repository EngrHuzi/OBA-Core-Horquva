import { Activity, ShieldAlert, ArrowRight, Info } from 'lucide-react';
import { ScenarioResult } from '../../lib/simulation';
import { RiskLevel } from '../../types';

interface ImpactSummaryProps {
  scenario: ScenarioResult;
}

const riskColor: Record<RiskLevel, string> = {
  critical: 'text-red-400',
  high: 'text-orange-400',
  medium: 'text-yellow-400',
  low: 'text-green-400',
};

const riskBg: Record<RiskLevel, string> = {
  critical: 'bg-red-500/10 border-red-500/20',
  high: 'bg-orange-500/10 border-orange-500/20',
  medium: 'bg-yellow-500/10 border-yellow-500/20',
  low: 'bg-green-500/10 border-green-500/20',
};

export function ImpactSummary({ scenario }: ImpactSummaryProps) {
  const scoreDrop = scenario.baselineHealthScore - scenario.simulatedHealthScore;
  const severity = scoreDrop >= 15 ? 'CRITICAL RISK' : scoreDrop >= 5 ? 'HIGH RISK' : 'MEDIUM RISK';
  const severityColor = scoreDrop >= 15 ? 'text-red-400' : scoreDrop >= 5 ? 'text-orange-400' : 'text-yellow-400';

  return (
    <div className="space-y-6 animate-fade-up">
      {/* Health Score Impact Card */}
      <div className="card p-6 relative overflow-hidden group">
        <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-purple-500 to-red-500/40"></div>
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-medium text-white flex items-center">
              <Activity className="w-5 h-5 text-purple-400 mr-2" />
              Organizational Health Impact
            </h3>
            <p className="text-sm text-slate-400 mt-1">
              Estimated drop if {scenario.type === 'PERSON_LEAVES' ? `${scenario.targetName} leaves` : `${scenario.targetName} fails`}
            </p>
          </div>
          <div className={`px-3 py-1 rounded-full border border-red-500/20 bg-red-500/10 ${severityColor} text-xs font-semibold tracking-wide`}>
            {severity}
          </div>
        </div>

        <div className="flex items-center space-x-6">
          <div className="text-center">
            <span className="text-xs text-slate-500 uppercase tracking-wider block mb-1">Before</span>
            <span className="text-3xl font-bold text-white">{scenario.baselineHealthScore}</span>
          </div>
          <ArrowRight className="w-6 h-6 text-slate-600" />
          <div className="text-center">
            <span className="text-xs text-slate-500 uppercase tracking-wider block mb-1">After</span>
            <span className={`text-4xl font-bold ${severityColor}`}>{scenario.simulatedHealthScore}</span>
          </div>
          <div className="ml-auto flex flex-col items-end">
             <span className="text-sm text-slate-400">Total Drop</span>
             <span className="text-2xl font-bold text-red-400">-{scoreDrop} pts</span>
          </div>
        </div>
      </div>

      {/* Impacted Agents List */}
      <div className="card p-6">
        <h3 className="text-lg font-medium text-white flex items-center mb-4">
          <ShieldAlert className="w-5 h-5 text-orange-400 mr-2" />
          Cascade Victims & Exposed Assets ({scenario.impactedAgents.length})
        </h3>
        
        {scenario.impactedAgents.length === 0 ? (
          <div className="text-center p-8 border border-dashed border-slate-700/50 rounded-lg">
            <Info className="w-8 h-8 text-slate-500 mx-auto mb-2" />
            <p className="text-sm text-slate-400">No agents directly impacted by this scenario.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {scenario.impactedAgents.map((impact, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-[#1a1a24] border border-slate-800">
                <div className="flex flex-col">
                  <span className="text-sm font-medium text-white">{impact.agentName}</span>
                  <span className="text-xs text-slate-500">{impact.reason}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className={`px-2 py-1 rounded text-[10px] uppercase tracking-wider border ${riskBg[impact.beforeRisk]} ${riskColor[impact.beforeRisk]}`}>
                    {impact.beforeRisk}
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-600" />
                  <div className={`px-2 py-1 rounded text-[10px] uppercase tracking-wider border ${riskBg[impact.afterRisk]} ${riskColor[impact.afterRisk]}`}>
                    {impact.afterRisk}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
