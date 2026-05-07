import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

type Message = {
  id: string;
  sender: 'ai' | 'customer';
  text: string;
};

export function TranscriptView({ messages }: { messages: Message[] }) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="glass-panel flex-1 flex flex-col overflow-hidden">
      <div className="p-4 border-b border-slate-700 bg-slate-800/50 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-slate-200">Live Transcript</h2>
        <div className="flex gap-2">
          <span className="flex items-center gap-1 text-[10px] text-blue-400 bg-blue-400/10 px-2 py-0.5 rounded border border-blue-400/20">Customer</span>
          <span className="flex items-center gap-1 text-[10px] text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded border border-emerald-400/20">VaaniAI</span>
        </div>
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth bg-slate-900/20">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-3">
             <div className="w-12 h-12 rounded-full border-2 border-slate-700 border-t-emerald-500 animate-spin"></div>
             <p className="text-sm font-medium">Waiting for conversation to start...</p>
          </div>
        )}
        {messages.map((msg) => {
          if (msg.sender === 'system' as any) {
            return (
              <div key={msg.id} className="flex justify-center">
                <span className="text-[10px] uppercase tracking-widest font-bold text-slate-500 bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700">
                  {msg.text}
                </span>
              </div>
            );
          }
          return (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={clsx(
                "flex",
                msg.sender === 'customer' ? "justify-end" : "justify-start"
              )}
            >
              <div
                className={clsx(
                  "max-w-[80%] rounded-2xl px-4 py-2 shadow-md transition-all",
                  msg.sender === 'customer'
                    ? "bg-blue-600/20 text-blue-100 border border-blue-500/30 rounded-br-none"
                    : "bg-slate-700/50 text-slate-200 border border-slate-600 rounded-bl-none"
                )}
              >
                <p className={clsx(
                  "text-[10px] opacity-70 mb-1 uppercase tracking-wider font-bold",
                  msg.sender === 'customer' ? "text-blue-400 text-right" : "text-emerald-400"
                )}>
                  {msg.sender === 'customer' ? 'Customer' : 'VaaniAI'}
                </p>
                <p className="text-sm md:text-base leading-relaxed font-medium">{msg.text}</p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
