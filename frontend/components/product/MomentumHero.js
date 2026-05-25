"use client";

import { motion } from "framer-motion";
import { Flame, HeartPulse, RotateCcw, ShieldCheck, Sparkles, Zap } from "lucide-react";

const toneStyles = {
  gold: "from-[#2f250f] via-[#121711] to-[#080807] border-zenGold/30",
  coral: "from-[#2a1710] via-[#101610] to-[#090807] border-coralGlow/30",
  sage: "from-[#10201b] via-[#101610] to-[#070907] border-zenSage/25",
  lime: "from-[#193016] via-[#101610] to-[#070907] border-limeGlow/25"
};

const icons = {
  celebration: Sparkles,
  comeback: RotateCcw,
  "streak-risk": Flame,
  "low-energy": HeartPulse,
  "high-energy": Zap,
  steady: ShieldCheck
};

export function MomentumHero({ momentum, userName, notice, error }) {
  const Icon = icons[momentum.type] || ShieldCheck;

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: "easeOut" }}
      className={`relative overflow-hidden rounded-[2rem] border bg-gradient-to-br p-6 md:p-8 ${toneStyles[momentum.tone] || toneStyles.sage}`}
    >
      <div className="absolute right-8 top-8 hidden h-28 w-28 rounded-full bg-white/10 blur-3xl md:block" />
      <div className="relative grid gap-8 lg:grid-cols-[1fr_300px] lg:items-end">
        <div>
          <p className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-3 py-1 text-sm font-semibold text-zenSage">
            <Icon className="h-4 w-4" />
            {momentum.label}
          </p>
          <h1 className="mt-5 max-w-4xl text-4xl font-semibold tracking-[-0.04em] md:text-6xl">
            {momentum.title}
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300">
            {momentum.subtitle}
          </p>
          <p className="mt-5 text-sm text-slate-400">For {userName || "today"}: focus on the next action, not a perfect day.</p>
          {notice ? <p className="mt-4 text-sm font-medium text-zenSage">{notice}</p> : null}
          {error ? <p className="mt-4 text-sm text-red-200">{error}</p> : null}
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1, duration: 0.35 }}
          className="rounded-3xl bg-zenCream p-5 text-[#121711] shadow-2xl"
        >
          <p className="text-sm text-slate-600">Best next step</p>
          <p className="mt-2 text-2xl font-semibold leading-8">{momentum.action}</p>
        </motion.div>
      </div>
    </motion.section>
  );
}
