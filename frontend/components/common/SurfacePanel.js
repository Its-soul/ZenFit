export function SurfacePanel({ children, className = "", as: Component = "section" }) {
  return <Component className={`panel rounded-[var(--radius-lg)] ${className}`}>{children}</Component>;
}
