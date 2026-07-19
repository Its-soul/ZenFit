"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Sparkles } from "lucide-react";

export function CelebrationToast({ message }) {
  return (
    <AnimatePresence>
      {message ? (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.96 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.96 }}
          role="status"
          aria-live="polite"
          className="fixed bottom-20 left-4 right-4 z-40 rounded-3xl bg-zenCream p-5 text-[#121711] shadow-[var(--shadow-md)] sm:bottom-6 sm:left-auto sm:max-w-sm"
        >
          <p className="flex items-center gap-2 text-sm font-semibold">
            <Sparkles className="h-4 w-4" />
            Momentum update
          </p>
          <p className="mt-1 text-sm leading-6 text-slate-700">{message}</p>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
