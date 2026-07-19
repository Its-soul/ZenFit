export function Input({ className = "", ...props }) {
  return (
    <input
      className={`w-full rounded-lg border border-white/10 bg-[#0b0f17] px-3 py-2.5 text-sm text-white outline-none transition-[border-color,box-shadow] placeholder:text-slate-500 focus-visible:border-zenSage focus-visible:ring-2 focus-visible:ring-zenSage/20 ${className}`}
      {...props}
    />
  );
}
