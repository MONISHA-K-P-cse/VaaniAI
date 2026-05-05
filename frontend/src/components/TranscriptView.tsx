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
      <div className="p-4 border-b border-slate-700 bg-slate-800/50">
        <h2 className="text-lg font-semibold text-slate-200">Live Transcript</h2>
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
        {messages.map((msg) => (
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
                "max-w-[80%] rounded-2xl px-4 py-2 shadow-md",
                msg.sender === 'customer'
                  ? "bg-blue-600/20 text-blue-100 border border-blue-500/30 rounded-br-none"
                  : "bg-slate-700/50 text-slate-200 border border-slate-600 rounded-bl-none"
              )}
            >
              <p className="text-xs opacity-50 mb-1 uppercase tracking-wider">
                {msg.sender === 'customer' ? 'Customer' : 'VaaniAI'}
              </p>
              <p className="text-sm md:text-base leading-relaxed">{msg.text}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
