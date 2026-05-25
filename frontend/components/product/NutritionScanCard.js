"use client";

import { motion } from "framer-motion";
import { Camera, CheckCircle2, ScanLine, Utensils } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

export function NutritionScanCard({ previewUrl, progress, analysis, form, onFile, onFormChange, onSave }) {
  return (
    <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="panel rounded-[1.75rem] p-6">
      <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <label className="group flex min-h-[340px] cursor-pointer flex-col items-center justify-center overflow-hidden rounded-[1.5rem] border border-dashed border-white/15 bg-[#151d16] text-center transition hover:border-zenSage">
          {previewUrl ? (
            <img src={previewUrl} alt="Meal preview" className="h-full min-h-[340px] w-full object-cover transition duration-500 group-hover:scale-105" />
          ) : (
            <div className="px-6">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-3xl bg-zenCream text-[#121711]">
                <Camera className="h-7 w-7" />
              </div>
              <h2 className="mt-5 text-3xl font-semibold tracking-[-0.02em]">Scan your meal first.</h2>
              <p className="mt-3 text-sm leading-6 text-muted">Take a photo. ZenFit estimates it, then you adjust only if needed.</p>
            </div>
          )}
          <input type="file" accept="image/*" capture="environment" className="hidden" onChange={onFile} />
        </label>

        <div>
          <p className="flex items-center gap-2 text-sm font-semibold text-zenSage">
            <ScanLine className="h-4 w-4" />
            Meal guidance
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-[-0.03em]">Good enough logging beats perfect tracking.</h1>
          <p className="mt-4 text-sm leading-6 text-muted">
            Nutrition should not feel like a spreadsheet. Scan, confirm, and move on with a simple next step.
          </p>

          {progress > 0 && !analysis ? (
            <div className="mt-5 rounded-2xl bg-[#151d16] p-4">
              <p className="text-sm font-semibold">Reading your meal...</p>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
                <div className="h-full rounded-full bg-zenSage" style={{ width: `${Math.max(progress, 12)}%` }} />
              </div>
            </div>
          ) : null}

          {analysis ? (
            <div className="mt-5 rounded-3xl bg-zenCream p-5 text-[#121711]">
              <p className="flex items-center gap-2 text-sm font-semibold">
                <CheckCircle2 className="h-4 w-4" />
                Meal estimate ready
              </p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <Input className="border-black/10 bg-white text-[#121711]" value={form.name} onChange={(event) => onFormChange({ ...form, name: event.target.value })} />
                <Input className="border-black/10 bg-white text-[#121711]" value={form.meal_type} onChange={(event) => onFormChange({ ...form, meal_type: event.target.value })} />
                <Input className="border-black/10 bg-white text-[#121711]" type="number" value={form.calories} onChange={(event) => onFormChange({ ...form, calories: Number(event.target.value) })} />
                <Input className="border-black/10 bg-white text-[#121711]" type="number" value={form.protein_g} onChange={(event) => onFormChange({ ...form, protein_g: Number(event.target.value) })} />
              </div>
              <p className="mt-4 text-sm leading-6 text-slate-700">{analysis.explanation}</p>
              <Button className="mt-5 bg-[#121711] text-white hover:bg-[#1f291d]" onClick={onSave}>
                <Utensils className="h-4 w-4" />
                Looks right
              </Button>
            </div>
          ) : (
            <div className="mt-5 rounded-3xl bg-[#151d16] p-5">
              <p className="font-semibold">After you scan</p>
              <p className="mt-2 text-sm leading-6 text-muted">ZenFit will suggest a simple nutrition next step, like protein, hydration, or an easier dinner choice.</p>
            </div>
          )}
        </div>
      </div>
    </motion.section>
  );
}
