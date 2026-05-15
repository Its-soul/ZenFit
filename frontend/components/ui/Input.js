export function Input({ className = "", ...props }) {
  return (
    <input
      className={`w-full rounded-lg border border-white/10 bg-[#0b0f17] px-3 py-2.5 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-white/30 focus:ring-2 focus:ring-white/10 ${className}`}
      {...props}
    />
  );
}
