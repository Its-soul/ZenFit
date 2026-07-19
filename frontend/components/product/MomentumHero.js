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
    <section className={`relative overflow-hidden rounded-[var(--radius-xl)] border bg-gradient-to-br p-[clamp(1.25rem,4vw,2rem)] ${toneStyles[momentum.tone] || toneStyles.sage}`}>
      <div className="relative grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(15rem,18rem)] lg:items-end">
        <div>
          <p className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-3 py-1 text-sm font-semibold text-zenSage">
            <Icon className="h-4 w-4" />
            {momentum.label}
          </p>
          <h1 className="mt-4 max-w-[18ch] text-[clamp(2rem,5vw,3.75rem)] font-semibold leading-[1.08] tracking-[-0.035em]">
            {momentum.title}
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300">
            {momentum.subtitle}
          </p>
          <p className="mt-4 text-sm text-slate-300">{userName ? `${userName}, focus` : "Focus"} on the next action—not a perfect day.</p>
          {notice ? <p role="status" className="status-banner status-banner--info mt-4">{notice}</p> : null}
          {error ? <p role="alert" className="status-banner status-banner--danger mt-4">{error}</p> : null}
        </div>

        <div className="rounded-[var(--radius-lg)] bg-zenCream p-5 text-[#121711] shadow-[var(--shadow-sm)]">
          <p className="text-sm font-medium text-slate-600">Your next step</p>
          <p className="mt-2 text-xl font-semibold leading-7 sm:text-2xl">{momentum.action}</p>
          <p className="mt-3 text-sm leading-6 text-slate-600">One useful action is enough for today.</p>
        </div>
      </div>
    </section>
  );
}
