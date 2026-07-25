export function Input({ className = "", ...props }) {
  return (
    <input
      className={`min-h-[var(--control-height)] w-full rounded-[var(--radius-sm)] border border-slate-700 bg-slate-950/80 px-3.5 py-2.5 text-base text-white outline-none transition-[border-color,box-shadow] placeholder:text-slate-500 focus-visible:border-zenSage focus-visible:ring-2 focus-visible:ring-zenSage/20 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...props}
    />
  );
}
