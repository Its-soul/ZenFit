export function Button({ children, className = "", variant = "primary", ...props }) {
  const variants = {
    primary: "bg-gradient-to-r from-emerald-300 via-teal-300 to-emerald-400 text-slate-950 shadow-[0_10px_26px_rgba(52,211,153,0.18)] hover:from-emerald-200 hover:to-teal-300",
    secondary: "border border-slate-700 bg-slate-800/70 text-white hover:border-emerald-400/30 hover:bg-slate-800",
    ghost: "bg-transparent text-slate-200 hover:bg-white/[0.07] hover:text-white",
    destructive: "border border-red-300/25 bg-red-400/10 text-red-100 hover:bg-red-400/15"
  };

  return (
    <button
      className={`inline-flex min-h-[var(--control-height)] items-center justify-center gap-2 rounded-[var(--radius-sm)] px-4 py-2.5 text-[0.9375rem] font-semibold outline-none transition-[background-color,border-color,color,opacity,transform,box-shadow] hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-zenSage focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 disabled:cursor-not-allowed disabled:translate-y-0 disabled:opacity-50 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
