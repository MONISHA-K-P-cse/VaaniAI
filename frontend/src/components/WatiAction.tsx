import { MessageCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export function WatiAction({ phoneNumber }: { phoneNumber: string }) {
  const handleWatiTrigger = () => {
    // Mocking the WATI API call
    console.log(`[WATI API MOCK] Triggering WhatsApp template message to ${phoneNumber}`);
    alert(`WhatsApp message triggered for ${phoneNumber} via WATI!`);
  };

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={handleWatiTrigger}
      className="flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg font-semibold shadow-lg transition-colors w-full sm:w-auto"
    >
      <MessageCircle size={20} />
      Send WhatsApp
    </motion.button>
  );
}
