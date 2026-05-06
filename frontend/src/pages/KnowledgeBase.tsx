import { useState, useEffect } from 'react';
import { Database, Search, FileText, ChevronRight } from 'lucide-react';

export function KnowledgeBase() {
  const [kbItems, setKbItems] = useState<any[]>([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/knowledge-base')
      .then(res => res.json())
      .then(data => setKbItems(data));
  }, []);

  return (
    <div className="p-6 flex flex-col gap-6 max-w-7xl mx-auto h-full">
      <header className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/50 backdrop-blur-md shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center shadow-lg shadow-amber-500/20">
            <Database className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
              Knowledge Base
            </h1>
            <p className="text-slate-400 text-sm mt-1">Manage the expertise powering VaaniAI RAG</p>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-3 glass-panel p-4 rounded-xl border border-slate-800 bg-slate-900/30 flex items-center gap-3">
          <Search className="text-slate-500" size={20} />
          <input 
            type="text" 
            placeholder="Search product expertise..." 
            className="bg-transparent border-none outline-none flex-1 text-slate-200 placeholder:text-slate-600"
          />
        </div>

        {kbItems.map((item) => (
          <div key={item.id} className="glass-panel p-6 rounded-2xl border border-slate-800 bg-slate-900/50 hover:border-amber-500/30 transition-all group flex flex-col gap-4">
            <div className="flex items-start justify-between">
              <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-amber-400 group-hover:bg-amber-500/20 transition-colors">
                <FileText size={20} />
              </div>
              <span className="text-[10px] font-bold text-slate-600 uppercase tracking-tighter bg-slate-800/50 px-2 py-1 rounded">Seeded</span>
            </div>
            <div>
              <h3 className="font-bold text-slate-200 text-lg mb-2">{item.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed line-clamp-3">{item.content}</p>
            </div>
            <button className="mt-auto flex items-center gap-1 text-xs font-bold text-amber-400 hover:text-amber-300 transition-colors uppercase tracking-widest">
              View Full Source <ChevronRight size={14} />
            </button>
          </div>
        ))}

        <div className="glass-panel p-6 rounded-2xl border border-dashed border-slate-700 bg-slate-900/10 flex flex-col items-center justify-center text-center gap-3 hover:bg-slate-800/20 transition-all cursor-pointer">
          <div className="w-12 h-12 rounded-full border border-dashed border-slate-600 flex items-center justify-center text-slate-500">
            +
          </div>
          <span className="text-slate-400 font-medium">Add New Knowledge</span>
          <p className="text-slate-600 text-xs">Upload PDF or Text to Pinecone</p>
        </div>
      </div>
    </div>
  );
}
