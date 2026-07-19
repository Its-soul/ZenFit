export function Field({ label, helper, error, children, className = "" }) {
  return (
    <label className={`min-w-0 ${className}`}>
      <span className="mb-1.5 block text-sm font-medium text-slate-200">{label}</span>
      {children}
      {helper ? <span className="mt-1.5 block text-sm leading-5 text-muted">{helper}</span> : null}
      {error ? <span className="mt-1.5 block text-sm leading-5 text-red-200">{error}</span> : null}
    </label>
  );
}
