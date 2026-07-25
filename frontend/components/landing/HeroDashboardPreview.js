import { Activity, HeartPulse, Salad, Sparkles } from "lucide-react";

const metrics = [
  { label: "Recovery", value: "Steady", icon: HeartPulse, tone: "text-emerald-300" },
  { label: "Workout", value: "38 min", icon: Activity, tone: "text-cyan-300" },
  { label: "Nutrition", value: "On track", icon: Salad, tone: "text-amber-300" }
];

export default function HeroDashboardPreview() {
  return (
    <div className="relative rounded-[2rem] border border-slate-700/80 bg-slate-900/90 p-4 shadow-2xl backdrop-blur-xl sm:p-5">
      <div className="flex items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-300">Daily overview</p>
          <h2 className="mt-1 text-xl font-black text-slate-100 sm:text-2xl">Your next useful step</h2>
        </div>
        <span className="rounded-full border border-emerald-400/25 bg-emerald-400/10 px-3 py-1 text-xs font-bold text-emerald-300">Ready</span>
      </div>

      <div className="mt-4 rounded-2xl border border-emerald-400/20 bg-gradient-to-br from-emerald-400/10 to-teal-400/5 p-5">
        <div className="flex items-start justify-between gap-4">
          <div><p className="text-xs text-slate-400">Today&apos;s training</p><p className="mt-1 text-lg font-bold text-slate-100">Full Body Foundation</p></div>
          <Activity className="h-5 w-5 text-emerald-300" />
        </div>
        <p className="mt-3 text-sm leading-6 text-slate-300">A moderate session that leaves room for recovery.</p>
        <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800"><div className="h-full w-3/4 rounded-full bg-gradient-to-r from-emerald-300 to-teal-400" /></div>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2 sm:gap-3">
        {metrics.map(({ label, value, icon: Icon, tone }) => (
          <div key={label} className="min-w-0 rounded-2xl border border-slate-800 bg-slate-950/70 p-3 sm:p-4">
            <Icon className={`h-4 w-4 ${tone}`} />
            <p className="mt-3 truncate text-[0.6875rem] text-slate-400 sm:text-xs">{label}</p>
            <p className="mt-1 truncate text-sm font-bold text-slate-100 sm:text-base">{value}</p>
          </div>
        ))}
      </div>

      <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-800/60 p-4">
        <p className="flex items-center gap-2 text-sm font-bold text-slate-100"><Sparkles className="h-4 w-4 text-emerald-300" />A calmer recommendation</p>
        <p className="mt-2 text-sm leading-6 text-slate-300">Keep today steady. Your plan can adjust again after the next check-in.</p>
      </div>
    </div>
  );
}
