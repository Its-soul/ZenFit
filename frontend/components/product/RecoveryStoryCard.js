"use client";

import { motion } from "framer-motion";
import { HeartPulse, Moon, MoveRight } from "lucide-react";

export function RecoveryStoryCard({ title, cause, effect, recommendation, tone = "sage", icon = "recovery" }) {
  const Icon = icon === "sleep" ? Moon : HeartPulse;
  const toneClass = tone === "coral" ? "text-coralGlow" : tone === "gold" ? "text-zenGold" : "text-zenSage";

  return (
    <motion.section initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="panel rounded-[1.5rem] p-6">
      <Icon className={`h-5 w-5 ${toneClass}`} />
      <h2 className="mt-4 text-2xl font-semibold tracking-[-0.02em]">{title}</h2>
      <div className="mt-5 grid gap-3">
        <div className="soft-panel rounded-2xl p-4">
          <p className="text-xs uppercase tracking-wide text-muted">Why it happened</p>
          <p className="mt-1 text-sm leading-6">{cause}</p>
        </div>
        <div className="soft-panel rounded-2xl p-4">
          <p className="text-xs uppercase tracking-wide text-muted">What it means</p>
          <p className="mt-1 text-sm leading-6">{effect}</p>
        </div>
        <div className="rounded-2xl bg-zenCream p-4 text-[#121711]">
          <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-slate-600">
            Next move
            <MoveRight className="h-3.5 w-3.5" />
          </p>
          <p className="mt-1 text-sm font-semibold leading-6">{recommendation}</p>
        </div>
      </div>
    </motion.section>
  );
}
