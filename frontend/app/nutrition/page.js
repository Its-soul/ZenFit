"use client";

import { Apple, Droplets, Search, Utensils } from "lucide-react";
import { useEffect, useState } from "react";
import Link from "next/link";

import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { createMeal, getTodayNutrition, lookupMeal } from "@/services/nutritionService";

function nutritionStory(nutrition) {
  const protein = nutrition?.protein_g || 0;
  const calories = nutrition?.calories || 0;
  const proteinTarget = nutrition?.protein_target_g || 0;
  if (proteinTarget && protein >= proteinTarget) return "Protein is supporting recovery today. Keep dinner simple and steady.";
  if (proteinTarget && protein >= proteinTarget * 0.55) return "You have a decent protein base. One more protein-forward meal would help training recovery.";
  if (calories > 0) return "You started the nutrition rhythm. Add protein next so the day feels more stable.";
  return "Start with a meal photo. Good enough logging beats perfect tracking.";
}

const emptyMealForm = { name: "", meal_type: "meal", calories: "0", protein_g: "0", carbs_g: "0", fat_g: "0" };

export default function NutritionPage() {
  const [nutrition, setNutrition] = useState(null);
  const [form, setForm] = useState(emptyMealForm);
  const [notice, setNotice] = useState("");
  const [manualOpen, setManualOpen] = useState(false);
  const [lookupQuery, setLookupQuery] = useState("");
  const [lookupLoading, setLookupLoading] = useState(false);

  async function loadNutrition() {
    setNutrition(await getTodayNutrition());
  }

  useEffect(() => {
    queueMicrotask(loadNutrition);
  }, []);

  async function saveMeal(payload = form) {
    await createMeal({
      ...payload,
      calories: Number(payload.calories),
      protein_g: Number(payload.protein_g),
      carbs_g: Number(payload.carbs_g),
      fat_g: Number(payload.fat_g)
    });
    setForm(emptyMealForm);
    setManualOpen(false);
    setNotice("Meal saved. This helps ZenFit guide the rest of your day.");
    await loadNutrition();
  }

  async function handleLookup(event) {
    event.preventDefault();
    if (!lookupQuery.trim()) return;
    setLookupLoading(true);
    try {
      const response = await lookupMeal(lookupQuery);
      setForm({
        ...response.estimate,
        calories: String(response.estimate.calories),
        protein_g: String(response.estimate.protein_g),
        carbs_g: String(response.estimate.carbs_g),
        fat_g: String(response.estimate.fat_g)
      });
      setManualOpen(true);
      setNotice("Review the USDA-backed lookup, make any quick edits, then save.");
    } finally {
      setLookupLoading(false);
    }
  }

  return (
    <ProtectedFeaturePage
      title="Nutrition"
      description="Use local meal analysis or log nutrition manually, then move on with a simple next step."
    >
      <Link href="/nutrition/meal-analysis" className="mb-5 inline-flex rounded-xl bg-zenCream px-4 py-2 text-sm font-semibold text-slate-950">Open local meal analysis</Link>
      {notice ? <p className="mt-4 text-sm text-zenSage">{notice}</p> : null}

      <section className="mt-5 grid gap-4 md:grid-cols-3">
        <div className="panel rounded-2xl p-5">
          <Apple className="h-5 w-5 text-coralGlow" />
          <p className="mt-4 text-sm text-muted">Today so far</p>
          <p className="mt-1 text-2xl font-semibold">{nutrition?.meals?.length || 0} meals logged</p>
        </div>
        <div className="panel rounded-2xl p-5">
          <Utensils className="h-5 w-5 text-zenSage" />
          <p className="mt-4 text-sm text-muted">Recovery support</p>
          <p className="mt-1 text-2xl font-semibold">{nutrition?.protein_g || 0}g protein</p>
        </div>
        <div className="panel rounded-2xl p-5">
          <Droplets className="h-5 w-5 text-zenGold" />
          <p className="mt-4 text-sm text-muted">Nutrition nudge</p>
          <p className="mt-1 text-sm leading-6">{nutritionStory(nutrition)}</p>
        </div>
      </section>

      <section className="mt-5 panel rounded-[1.5rem] p-5">
        <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
          <div>
            <p className="font-semibold">Need to log without a photo?</p>
            <p className="mt-1 text-sm text-muted">Manual entry is here when you need it, but it stays out of the way.</p>
          </div>
          <Button variant="secondary" onClick={() => setManualOpen((value) => !value)}>
            {manualOpen ? "Hide manual entry" : "Manual entry"}
          </Button>
        </div>

        <form className="mt-5 flex flex-col gap-3 sm:flex-row" onSubmit={handleLookup}>
          <Input
            placeholder="Try 100g chicken breast, 2 eggs, 1 cup rice"
            value={lookupQuery}
            onChange={(event) => setLookupQuery(event.target.value)}
          />
          <Button variant="secondary" disabled={lookupLoading}>
            <Search className="h-4 w-4" />
            {lookupLoading ? "Looking up..." : "Lookup"}
          </Button>
        </form>

        {manualOpen ? (
          <form
            className="mt-5 grid gap-3 rounded-2xl border border-white/10 bg-[#0d120e] p-4 md:grid-cols-6"
            onSubmit={(event) => {
              event.preventDefault();
              saveMeal();
            }}
          >
            <Input placeholder="Meal name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
            <Input value={form.meal_type} onChange={(event) => setForm({ ...form, meal_type: event.target.value })} />
            <Input aria-label="Calories" inputMode="numeric" value={form.calories} onChange={(event) => /^\d*$/.test(event.target.value) && setForm({ ...form, calories: event.target.value })} />
            <Input aria-label="Protein grams" inputMode="decimal" value={form.protein_g} onChange={(event) => /^\d*(?:\.\d*)?$/.test(event.target.value) && setForm({ ...form, protein_g: event.target.value })} />
            <Input aria-label="Carbohydrate grams" inputMode="decimal" value={form.carbs_g} onChange={(event) => /^\d*(?:\.\d*)?$/.test(event.target.value) && setForm({ ...form, carbs_g: event.target.value })} />
            <Input aria-label="Fat grams" inputMode="decimal" value={form.fat_g} onChange={(event) => /^\d*(?:\.\d*)?$/.test(event.target.value) && setForm({ ...form, fat_g: event.target.value })} />
            <Button>Add meal</Button>
          </form>
        ) : null}
      </section>

      <div className="mt-5 space-y-3">
        {(nutrition?.meals || []).map((meal) => (
          <div key={meal.id} className="panel rounded-2xl p-4">
            <p className="font-semibold">{meal.name}</p>
            <p className="mt-1 text-sm text-muted">{meal.calories} kcal / {meal.protein_g}g protein</p>
            {meal.analysis_explanation ? <p className="mt-2 text-xs text-muted">{meal.analysis_explanation}</p> : null}
          </div>
        ))}
      </div>
    </ProtectedFeaturePage>
  );
}
