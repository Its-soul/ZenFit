export function GlassPanel({ children, className = "" }) {
  return <section className={`panel rounded-xl ${className}`}>{children}</section>;
}
