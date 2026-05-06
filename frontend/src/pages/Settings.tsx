import { Settings as SettingsIcon, Shield, Cpu, Zap, Sliders } from 'lucide-react';

export function Settings() {
  return (
    <div className="p-6 flex flex-col gap-6 max-w-7xl mx-auto h-full">
      <header className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/50 backdrop-blur-md shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-slate-600 to-slate-800 flex items-center justify-center shadow-lg shadow-slate-900/50">
            <SettingsIcon className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-slate-200 to-slate-400 bg-clip-text text-transparent">
              System Settings
            </h1>
            <p className="text-slate-400 text-sm mt-1">Configure AI models, APIs, and voice personas</p>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Model Config */}
        <section className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/50 space-y-6">
          <div className="flex items-center gap-2 mb-4">
            <Cpu className="text-emerald-400" size={20} />
            <h2 className="text-lg font-bold text-slate-200">AI Model Configuration</h2>
          </div>
          <div className="space-y-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-slate-500 uppercase">Active Live Model</label>
              <select className="bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-200 outline-none">
                <option>Gemini 2.0 Flash (Live)</option>
                <option>Gemini 1.5 Pro</option>
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-slate-500 uppercase">Reasoning Model (RAG)</label>
              <select className="bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-sm text-slate-200 outline-none">
                <option>Gemini 2.0 Flash</option>
                <option>Gemini 1.5 Pro</option>
              </select>
            </div>
          </div>
        </section>

        {/* API Status */}
        <section className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/50 space-y-6">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="text-cyan-400" size={20} />
            <h2 className="text-lg font-bold text-slate-200">API Health & Status</h2>
          </div>
          <div className="space-y-3">
            {[
              { name: 'Gemini Multimodal Live', status: 'Healthy', lat: '120ms' },
              { name: 'Pinecone Serverless', status: 'Healthy', lat: '45ms' },
              { name: 'Twilio Stream Hook', status: 'Standby', lat: '-' },
              { name: 'WATI WhatsApp API', status: 'Mock Mode', lat: '0ms' },
            ].map((api) => (
              <div key={api.name} className="flex items-center justify-between p-3 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <div>
                  <p className="text-sm font-medium text-slate-300">{api.name}</p>
                  <p className="text-[10px] text-slate-500 font-mono">LATENCY: {api.lat}</p>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${api.status === 'Healthy' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-700 text-slate-400'}`}>
                  {api.status}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Voice Persona */}
        <section className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/50 space-y-6">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="text-amber-400" size={20} />
            <h2 className="text-lg font-bold text-slate-200">Voice Persona (Puck)</h2>
          </div>
          <div className="space-y-4">
             <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Empathy Level</span>
                <input type="range" className="accent-amber-500 w-1/2" defaultValue={80} />
             </div>
             <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Response Speed</span>
                <input type="range" className="accent-amber-500 w-1/2" defaultValue={95} />
             </div>
             <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Language Flexibility</span>
                <input type="range" className="accent-amber-500 w-1/2" defaultValue={100} />
             </div>
          </div>
        </section>

        {/* System Advanced */}
        <section className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/50 space-y-6">
          <div className="flex items-center gap-2 mb-4">
            <Sliders className="text-slate-400" size={20} />
            <h2 className="text-lg font-bold text-slate-200">Advanced Controls</h2>
          </div>
          <div className="grid grid-cols-2 gap-4">
             <button className="p-4 rounded-xl border border-slate-700 hover:bg-slate-800 transition-all text-xs font-bold uppercase tracking-widest text-slate-400">
               Reset Database
             </button>
             <button className="p-4 rounded-xl border border-slate-700 hover:bg-slate-800 transition-all text-xs font-bold uppercase tracking-widest text-slate-400">
               Flush Cache
             </button>
             <button className="p-4 rounded-xl border border-rose-900/30 bg-rose-900/10 hover:bg-rose-900/20 transition-all text-xs font-bold uppercase tracking-widest text-rose-400 col-span-2">
               Danger Zone: Purge Pinecone
             </button>
          </div>
        </section>
      </div>
    </div>
  );
}
