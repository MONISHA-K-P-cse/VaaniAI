import { motion } from 'framer-motion';
import { CheckCircle, ListTodo, FileText, Send } from 'lucide-react';

export function PostCallSummary({ data }: { data: any }) {
  if (!data) return (
    <div className="glass-panel flex-1 flex items-center justify-center">
      <div className="animate-pulse flex flex-col items-center gap-4">
        <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400">VaaniAI is analyzing the call...</p>
      </div>
    </div>
  );

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-panel flex-1 flex flex-col overflow-y-auto p-6 space-y-6"
    >
      <div className="border-b border-slate-700 pb-4">
        <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <FileText className="text-cyan-400" /> Post-Call Intelligence
        </h2>
      </div>

      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-emerald-400 flex items-center gap-2">
          <CheckCircle size={18} /> Executive Summary
        </h3>
        <p className="text-slate-300 leading-relaxed bg-slate-800/50 p-4 rounded-lg border border-slate-700">
          {data.summary}
        </p>
      </div>

      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-amber-400 flex items-center gap-2">
          <ListTodo size={18} /> Actionable Next Steps
        </h3>
        <ul className="list-disc pl-5 text-slate-300 space-y-2 bg-slate-800/50 p-4 rounded-lg border border-slate-700">
          {data.next_steps.map((step: string, i: number) => (
            <li key={i}>{step}</li>
          ))}
        </ul>
      </div>

      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-blue-400 flex items-center gap-2">
          <Send size={18} /> Automated Follow-Up (WhatsApp)
        </h3>
        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700 relative">
          {data.whatsapp_sent && (
            <span className="absolute top-4 right-4 bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded text-xs font-bold border border-emerald-500/30">
              SENT ✓
            </span>
          )}
          <p className="text-slate-300 italic whitespace-pre-wrap pr-16">{data.whatsapp_message}</p>
        </div>
      </div>
    </motion.div>
  );
}
