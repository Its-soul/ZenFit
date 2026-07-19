export default function HeroDashboardPreview() {
  const metrics = [["Streak", "4"], ["Recovery", "82"], ["Protein", "96g"]];

  return (
    <div className="zen-card w-full rounded-[clamp(1.5rem,3vw,2rem)] p-[clamp(0.875rem,2vw,1.25rem)]">
      <div className="rounded-[clamp(1.125rem,2.5vw,1.5rem)] bg-[#121711] p-[clamp(1rem,2.5vw,1.25rem)] text-white">
        <div className="flex items-center justify-between gap-4">
          <div className="min-w-0">
            <p className="text-sm text-slate-300">Today</p>
            <h2 className="text-xl font-semibold sm:text-2xl">Stay on track</h2>
          </div>
          <span className="shrink-0 rounded-full bg-zenSage px-3 py-1 text-xs font-semibold text-[#121711]">Ready</span>
        </div>
        <div className="mt-5 grid gap-3 sm:mt-6">
          <div className="rounded-2xl bg-white/10 p-4">
            <p className="text-sm text-slate-300">Workout</p>
            <p className="mt-1 text-base font-semibold sm:text-lg">Full Body Strength</p>
            <p className="mt-1 text-sm text-slate-300">38 min · Moderate · 5 exercises</p>
          </div>
          <div className="grid grid-cols-3 gap-2 sm:gap-3">
            {metrics.map(([label, value]) => (
              <div key={label} className="min-w-0 rounded-2xl bg-white/10 p-3 sm:p-4">
                <p className="truncate text-[0.6875rem] text-slate-300 sm:text-xs">{label}</p>
                <p className="mt-1 text-xl font-semibold sm:text-2xl">{value}</p>
              </div>
            ))}
          </div>
          <div className="rounded-2xl bg-[#f5f1e8] p-4 text-[#121711]">
            <p className="text-sm font-semibold">Daily Insight</p>
            <p className="mt-1 text-sm leading-6 text-slate-700">You recover better after 8+ hours of sleep. Keep today steady, not intense.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
