"use client";

import { motion } from "framer-motion";
import { X } from "lucide-react";

export function ActionSheet({ open, title, children, onClose }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 px-4 pb-4 md:items-center md:pb-0" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <motion.div
        role="dialog"
        aria-modal="true"
        aria-labelledby="action-sheet-title"
        initial={{ opacity: 0, y: 28, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        className="panel w-full max-w-lg rounded-[1.5rem] p-5"
      >
        <div className="flex items-center justify-between">
          <h2 id="action-sheet-title" className="text-lg font-semibold">{title}</h2>
          <button type="button" aria-label="Close dialog" onClick={onClose} className="inline-flex h-11 w-11 items-center justify-center rounded-full text-slate-300 outline-none hover:bg-white/10 hover:text-white focus-visible:ring-2 focus-visible:ring-zenSage">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="mt-4">{children}</div>
      </motion.div>
    </div>
  );
}
