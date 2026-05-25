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
          className="fixed bottom-6 right-6 z-40 max-w-sm rounded-3xl bg-zenCream p-5 text-[#121711] shadow-2xl"
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
