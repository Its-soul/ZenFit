"use client";

import { motion } from "framer-motion";

export function MomentumStrip({ narratives }) {
  return (
    <section className="grid gap-3 md:grid-cols-3">
      {narratives.map((item, index) => (
        <motion.div
          key={item.label}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.06 }}
          className="panel rounded-2xl p-5"
        >
          <p className="text-sm text-muted">{item.label}</p>
          <p className="mt-2 text-xl font-semibold leading-7">{item.value}</p>
          <p className="mt-2 text-sm text-muted">{item.helper}</p>
        </motion.div>
      ))}
    </section>
  );
}
