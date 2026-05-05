import { clsx } from 'clsx';
import { motion } from 'framer-motion';

export function LeadBadge({ score }: { score: number }) {
  const getScoreColor = (s: number) => {
    if (s >= 8) return "bg-green-500/20 text-green-400 border-green-500/50 shadow-[0_0_10px_rgba(34,197,94,0.3)]";
    if (s >= 5) return "bg-orange-500/20 text-orange-400 border-orange-500/50 shadow-[0_0_10px_rgba(249,115,22,0.3)]";
    return "bg-red-500/20 text-red-400 border-red-500/50 shadow-[0_0_10px_rgba(239,68,68,0.3)]";
  };

  return (
    <motion.div 
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className={clsx(
        "px-3 py-1 rounded-full border text-sm font-bold flex items-center gap-2",
        getScoreColor(score)
      )}
    >
      <div className={clsx("w-2 h-2 rounded-full animate-pulse", score >= 8 ? "bg-green-400" : score >= 5 ? "bg-orange-400" : "bg-red-400")} />
      Score: {score}/10
    </motion.div>
  );
}
