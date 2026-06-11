import { getDataset } from '../../lib/data';
import { OwnershipOverview } from '../../components/ownership/OwnershipOverview';
import { ConcentrationBar } from '../../components/ownership/ConcentrationBar';
import { OwnershipList } from '../../components/ownership/OwnershipList';

export default function OwnershipPage() {
  const dataset = getDataset();

  return (
    <div className="space-y-6 animate-in fade-in duration-500 pb-10">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white tracking-tight">Ownership Intelligence</h1>
        <p className="text-slate-400 mt-1">Human-agent dependency map identifying single points of failure and coverage gaps.</p>
      </div>

      <OwnershipOverview agents={dataset.agents} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="col-span-1 lg:col-span-2">
            <ConcentrationBar agents={dataset.agents} />
        </div>
      </div>

      <OwnershipList agents={dataset.agents} />
    </div>
  );
}
