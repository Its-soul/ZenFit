"use client";

import { Apple, Droplets, Utensils } from "lucide-react";
import { useEffect, useState } from "react";

import { NutritionScanCard } from "@/components/product/NutritionScanCard";
import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { analyzeMealImage, createMeal, getTodayNutrition } from "@/services/nutritionService";

function nutritionStory(nutrition) {
  const protein = nutrition?.protein_g || 0;
  const calories = nutrition?.calories || 0;
  if (protein >= 110) return "Protein is supporting recovery today. Keep dinner simple and steady.";
  if (protein >= 60) return "You have a decent protein base. One more protein-forward meal would help training recovery.";
  if (calories > 0) return "You started the nutrition rhythm. Add protein next so the day feels more stable.";
  return "Start with a meal photo. Good enough logging beats perfect tracking.";
}

export default function NutritionPage() {
  const [nutrition, setNutrition] = useState(null);
  const [form, setForm] = useState({ name: "", meal_type: "meal", calories: 500, protein_g: 30, carbs_g: 50, fat_g: 15 });
  const [previewUrl, setPreviewUrl] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [notice, setNotice] = useState("");
  const [manualOpen, setManualOpen] = useState(false);

  async function loadNutrition() {
    setNutrition(await getTodayNutrition());
  }

  useEffect(() => {
    loadNutrition();
  }, []);

  async function saveMeal(payload = form) {
    await createMeal(payload);
    setForm({ name: "", meal_type: "meal", calories: 500, protein_g: 30, carbs_g: 50, fat_g: 15 });
    setAnalysis(null);
    setPreviewUrl("");
    setManualOpen(false);
    setNotice("Meal saved. This helps ZenFit guide the rest of your day.");
    await loadNutrition();
  }

  async function handleImageChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setPreviewUrl(URL.createObjectURL(file));
    setUploadProgress(1);
    const response = await analyzeMealImage(file, setUploadProgress);
    setAnalysis(response);
    setForm({
      ...response.estimate,
      calories: response.estimate.calories,
      protein_g: response.estimate.protein_g,
      carbs_g: response.estimate.carbs_g,
      fat_g: response.estimate.fat_g
    });
    setNotice("Review the estimate, make any quick edits, then save.");
  }

  return (
    <ProtectedFeaturePage
      title="Nutrition"
      description="Scan first, adjust only when needed, and move on with a simple next step."
    >
      <NutritionScanCard
        previewUrl={previewUrl}
        progress={uploadProgress}
        analysis={analysis}
        form={form}
        onFile={handleImageChange}
        onFormChange={setForm}
        onSave={() => saveMeal()}
      />

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
            <Input type="number" value={form.calories} onChange={(event) => setForm({ ...form, calories: Number(event.target.value) })} />
            <Input type="number" value={form.protein_g} onChange={(event) => setForm({ ...form, protein_g: Number(event.target.value) })} />
            <Input type="number" value={form.carbs_g} onChange={(event) => setForm({ ...form, carbs_g: Number(event.target.value) })} />
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
