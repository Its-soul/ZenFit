"use client";

import { motion } from "framer-motion";
import { BatteryLow, Flame, HeartPulse, SmilePlus, Zap } from "lucide-react";

import { Button } from "@/components/ui/Button";

const moods = [
  { id: "drained", label: "Drained", energy: 3, stress: 8, motivation: 3, icon: BatteryLow, response: "We'll keep it light." },
  { id: "okay", label: "Okay", energy: 6, stress: 5, motivation: 5, icon: SmilePlus, response: "Steady is enough." },
  { id: "focused", label: "Focused", energy: 7, stress: 4, motivation: 8, icon: HeartPulse, response: "Good day to execute." },
  { id: "strong", label: "Strong", energy: 9, stress: 3, motivation: 8, icon: Zap, response: "Push with control." },
  { id: "motivated", label: "Motivated", energy: 8, stress: 3, motivation: 10, icon: Flame, response: "Use the spark today." }
];

export function DailyCheckInCard({ selectedMood, onSelectMood, onSave }) {
  const mood = moods.find((item) => item.id === selectedMood) || moods[1];

  return (
    <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="panel rounded-[1.5rem] p-6">
      <p className="text-sm font-semibold text-zenSage">Daily check-in</p>
      <h2 className="mt-2 text-2xl font-semibold">How does today feel?</h2>
      <p className="mt-2 text-sm text-muted">One tap is enough. ZenFit adjusts the tone around your answer.</p>

      <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-5">
        {moods.map((item) => {
          const Icon = item.icon;
          const active = selectedMood === item.id;
          return (
            <motion.button
              type="button"
              aria-pressed={active}
              whileTap={{ scale: 0.97 }}
              key={item.id}
              onClick={() => onSelectMood(item)}
              className={`min-h-24 rounded-2xl border p-4 text-left outline-none transition-[background-color,border-color,color,transform] focus-visible:ring-2 focus-visible:ring-zenSage ${
                active ? "border-zenSage bg-zenSage text-[#121711]" : "border-white/10 bg-[#151d16] text-slate-200 hover:border-white/25"
              }`}
            >
              <Icon className="h-5 w-5" />
              <p className="mt-3 text-sm font-semibold">{item.label}{active ? <span className="sr-only">, selected</span> : null}</p>
            </motion.button>
          );
        })}
      </div>

      <div className="mt-5 rounded-2xl bg-[#151d16] p-4">
        <p className="text-sm font-semibold">{mood.response}</p>
        <p className="mt-1 text-sm text-muted">This check-in helps ZenFit protect momentum without making today feel like work.</p>
      </div>

      <Button className="mt-5 w-full" onClick={() => onSave(mood)}>
        Save how I feel
      </Button>
    </motion.section>
  );
}
