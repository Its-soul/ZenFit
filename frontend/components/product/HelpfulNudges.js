"use client";

import { motion } from "framer-motion";

import { Button } from "@/components/ui/Button";

export function HelpfulNudges({ items, onFeedback }) {
  const nudges = (items || []).slice(0, 3);

  if (!nudges.length) {
    return (
      <section className="panel rounded-[1.5rem] p-6">
        <p className="text-sm font-semibold text-zenSage">Helpful nudge</p>
        <p className="mt-2 text-lg font-semibold">Start with one small action.</p>
        <p className="mt-2 text-sm text-muted">ZenFit gets more personal as you log workouts, meals, sleep, and recovery.</p>
      </section>
    );
  }

  return (
    <section className="panel rounded-[1.5rem] p-6">
      <p className="text-sm font-semibold text-zenSage">Helpful nudges</p>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {nudges.map((item, index) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="soft-panel rounded-2xl p-4"
          >
            <p className="font-semibold">{item.title}</p>
            <p className="mt-2 text-sm leading-6 text-muted">{item.body}</p>
            {item.reasoning_summary ? <p className="mt-3 text-xs leading-5 text-slate-400">{item.reasoning_summary}</p> : null}
            <div className="mt-4 flex gap-2">
              <Button variant="secondary" className="px-3 py-1.5 text-xs" onClick={() => onFeedback(item.id, "accepted")}>
                I'll do this
              </Button>
              <Button variant="ghost" className="px-3 py-1.5 text-xs" onClick={() => onFeedback(item.id, "dismissed")}>
                Not today
              </Button>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
