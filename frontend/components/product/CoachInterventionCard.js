"use client";

import { motion } from "framer-motion";
import { Bot, Send, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

const prompts = ["I'm tired today", "Shorten my workout", "What should I eat?", "Keep me accountable", "I missed yesterday"];

export function CoachInterventionCard({ momentum, reply, input, loading, onInputChange, onAsk }) {
  return (
    <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="panel rounded-[1.5rem] p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="flex items-center gap-2 text-sm font-semibold text-zenSage">
            <Bot className="h-4 w-4" />
            Coach intervention
          </p>
          <h2 className="mt-2 text-2xl font-semibold">Protect momentum.</h2>
        </div>
        <Sparkles className="h-5 w-5 text-zenGold" />
      </div>

      <div className="mt-5 rounded-3xl bg-zenCream p-5 text-[#121711]">
        <p className="text-sm font-semibold">{momentum.label}</p>
        <p className="mt-2 text-sm leading-6 text-slate-700">
          {loading && !reply ? "Thinking about your best next step..." : reply}
        </p>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {[momentum.coachPrompt, ...prompts].filter(Boolean).slice(0, 6).map((prompt) => (
          <button
            key={prompt}
            onClick={() => onAsk(prompt)}
            className="rounded-full border border-white/10 px-3 py-1.5 text-xs text-slate-200 transition hover:border-zenSage hover:text-white"
          >
            {prompt}
          </button>
        ))}
      </div>

      <form
        className="mt-4 flex gap-2"
        onSubmit={(event) => {
          event.preventDefault();
          onAsk();
        }}
      >
        <Input value={input} onChange={(event) => onInputChange(event.target.value)} placeholder="Tell your coach what is hard today..." />
        <Button disabled={loading}>
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </motion.section>
  );
}
