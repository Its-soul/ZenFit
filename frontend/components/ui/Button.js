export function Button({ children, className = "", variant = "primary", ...props }) {
  const variants = {
    primary: "bg-white text-slate-950 hover:bg-slate-200",
    secondary: "border border-white/10 bg-white/10 text-white hover:bg-white/15",
    ghost: "bg-transparent text-slate-200 hover:bg-white/10"
  };

  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-60 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
