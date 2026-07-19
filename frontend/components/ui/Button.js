export function Button({ children, className = "", variant = "primary", ...props }) {
  const variants = {
    primary: "bg-zenCream text-[#151a15] shadow-[0_8px_22px_rgba(0,0,0,0.14)] hover:bg-white",
    secondary: "border border-white/15 bg-white/[0.07] text-white hover:border-white/25 hover:bg-white/10",
    ghost: "bg-transparent text-slate-200 hover:bg-white/[0.07] hover:text-white",
    destructive: "border border-red-300/25 bg-red-400/10 text-red-100 hover:bg-red-400/15"
  };

  return (
    <button
      className={`inline-flex min-h-[var(--control-height)] items-center justify-center gap-2 rounded-[var(--radius-sm)] px-4 py-2.5 text-[0.9375rem] font-semibold outline-none transition-[background-color,border-color,color,opacity,transform,box-shadow] focus-visible:ring-2 focus-visible:ring-zenSage focus-visible:ring-offset-2 focus-visible:ring-offset-[#101610] disabled:cursor-not-allowed disabled:opacity-50 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
