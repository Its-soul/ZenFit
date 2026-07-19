import { memo } from "react";

function NumericTextField({ field, label, value, error, integer = false, onChange, onBlur }) {
  const errorId = `${field}-error`;

  return (
    <label className="min-w-0">
      <span className="mb-2 block text-sm text-slate-200">{label}</span>
      <input
        aria-describedby={error ? errorId : undefined}
        aria-invalid={Boolean(error)}
        autoComplete="off"
        className="w-full rounded-lg border border-white/10 bg-[#0b0f17] px-3 py-2.5 text-sm text-white outline-none transition-[border-color,box-shadow] focus-visible:border-zenSage focus-visible:ring-2 focus-visible:ring-zenSage/20 aria-[invalid=true]:border-red-400"
        inputMode={integer ? "numeric" : "decimal"}
        name={field}
        type="text"
        value={value}
        onBlur={() => onBlur(field)}
        onChange={(event) => onChange(field, event.target.value, integer)}
      />
      {error ? <span id={errorId} className="mt-1.5 block text-xs text-red-300">{error}</span> : null}
    </label>
  );
}

export default memo(NumericTextField);
