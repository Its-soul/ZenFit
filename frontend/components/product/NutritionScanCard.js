"use client";

import { motion } from "framer-motion";
import { Camera, CheckCircle2, ScanLine, Utensils } from "lucide-react";

import { Button } from "@/components/ui/Button";

const resultInputStyle = {
  backgroundColor: "#ffffff",
  color: "#121711",
  WebkitTextFillColor: "#121711"
};

function EstimateInput({ label, value, suffix = "", ...props }) {
  const displayValue = value === "" || value == null ? "Not set" : value;

  return (
    <label className="block rounded-2xl border border-[#8FE8C5]/35 bg-[#121711] p-4 shadow-sm">
      <span className="block text-[11px] font-semibold uppercase tracking-[0.08em] text-zenSage">{label}</span>
      <span className="mt-2 block min-h-7 truncate text-2xl font-semibold leading-7 text-white">
        {displayValue}
        {suffix}
      </span>
      <input
        className="mt-3 w-full rounded-lg border border-white/20 px-3 py-2 text-sm font-semibold outline-none transition focus:border-[#47745f] focus:ring-2 focus:ring-[#8FE8C5]/35"
        style={resultInputStyle}
        value={value}
        {...props}
      />
    </label>
  );
}

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
            <div className="mt-5 rounded-3xl bg-zenCream p-5 text-[#121711] shadow-[0_18px_45px_rgba(0,0,0,0.18)]">
              <p className="flex items-center gap-2 text-sm font-semibold text-[#263525]">
                <CheckCircle2 className="h-4 w-4 text-[#47745f]" />
                Meal estimate ready
              </p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <EstimateInput label="Meal" value={form.name} onChange={(event) => onFormChange({ ...form, name: event.target.value })} />
                <EstimateInput label="Type" value={form.meal_type} onChange={(event) => onFormChange({ ...form, meal_type: event.target.value })} />
                <EstimateInput
                  label="Calories"
                  type="number"
                  value={form.calories}
                  suffix=" kcal"
                  onChange={(event) => onFormChange({ ...form, calories: Number(event.target.value) })}
                />
                <EstimateInput
                  label="Protein (g)"
                  type="number"
                  value={form.protein_g}
                  suffix="g"
                  onChange={(event) => onFormChange({ ...form, protein_g: Number(event.target.value) })}
                />
                <EstimateInput
                  label="Carbs (g)"
                  type="number"
                  value={form.carbs_g}
                  suffix="g"
                  onChange={(event) => onFormChange({ ...form, carbs_g: Number(event.target.value) })}
                />
                <EstimateInput
                  label="Fat (g)"
                  type="number"
                  value={form.fat_g}
                  suffix="g"
                  onChange={(event) => onFormChange({ ...form, fat_g: Number(event.target.value) })}
                />
              </div>
              {analysis.detected_items?.length ? (
                <div className="mt-4 flex flex-wrap gap-2">
                  {analysis.detected_items.map((item) => (
                    <span key={`${item.name}-${item.grams}`} className="rounded-full bg-[#121711]/10 px-3 py-1 text-xs font-semibold text-[#263525]">
                      {item.name} / {item.grams}g
                    </span>
                  ))}
                </div>
              ) : null}
              <p className="mt-4 text-sm leading-6 text-slate-800">{analysis.explanation}</p>
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
