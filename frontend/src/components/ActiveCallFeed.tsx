import { PhoneCall, User, Plus } from 'lucide-react';
import { clsx } from 'clsx';

type Call = {
  id: string;
  customerName: string;
  phone: string;
  duration: string;
  isActive: boolean;
};

export function ActiveCallFeed({ calls, activeId, onSelect, onSimulate }: { calls: Call[], activeId: string, onSelect: (id: string) => void, onSimulate: () => void }) {
  return (
    <div className="glass-panel w-full md:w-80 flex flex-col h-[30vh] md:h-auto overflow-hidden flex-shrink-0">
      <div className="p-4 border-b border-slate-700 bg-slate-800/50 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
          <PhoneCall size={20} className="text-emerald-400" />
          Active Calls
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={onSimulate}
            className="p-1.5 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500 hover:text-white rounded-lg transition-all border border-emerald-500/20"
            title="Simulate New Call"
          >
            <Plus size={16} />
          </button>
          <span className="bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full text-xs font-bold border border-emerald-500/30">
            {calls.length}
          </span>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {calls.map(call => (
          <button
            key={call.id}
            onClick={() => onSelect(call.id)}
            className={clsx(
              "w-full text-left p-3 rounded-lg border transition-all duration-200 group",
              activeId === call.id
                ? "bg-slate-700/80 border-slate-500 shadow-md"
                : "bg-slate-800/30 border-transparent hover:bg-slate-700/40"
            )}
          >
            <div className="flex justify-between items-start mb-1">
              <div className="font-medium text-slate-200 flex items-center gap-2">
                <User size={16} className="text-slate-400" />
                {call.customerName}
              </div>
              <div className="text-xs text-slate-400 bg-slate-900/50 px-2 py-1 rounded-md">
                {call.duration}
              </div>
            </div>
            <div className="text-sm text-slate-400 ml-6">
              {call.phone}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
