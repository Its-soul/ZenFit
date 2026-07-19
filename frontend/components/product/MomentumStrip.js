export function MomentumStrip({ narratives }) {
  return (
    <section className="grid gap-3 md:grid-cols-3">
      {narratives.map((item) => (
        <div
          key={item.label}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="panel rounded-[var(--radius-md)] p-5"
        >
          <p className="text-sm text-muted">{item.label}</p>
          <p className="mt-2 text-xl font-semibold leading-7">{item.value}</p>
          <p className="mt-2 text-sm text-muted">{item.helper}</p>
        </div>
      ))}
    </section>
  );
}
