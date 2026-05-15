import { motion } from "framer-motion";

export function MetricCard({ label, value, helper, tone = "cyan", icon: Icon }) {
  const tones = {
    cyan: "text-cyanGlow",
    lime: "text-limeGlow",
    coral: "text-coralGlow",
    white: "text-white"
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="panel rounded-xl p-5"
    >
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted">{label}</p>
        {Icon ? <Icon className={`h-5 w-5 ${tones[tone]}`} /> : null}
      </div>
      <div className="mt-4 text-3xl font-semibold tracking-normal text-white">{value}</div>
      <p className="mt-2 text-sm text-muted">{helper}</p>
    </motion.div>
  );
}
