"use client";

import { Camera, CheckCircle2, Upload } from "lucide-react";
import { useEffect, useState } from "react";

import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { analyzeMealImage, createMeal, getTodayNutrition } from "@/services/nutritionService";

export default function NutritionPage() {
  const [nutrition, setNutrition] = useState(null);
  const [form, setForm] = useState({ name: "", meal_type: "meal", calories: 500, protein_g: 30, carbs_g: 50, fat_g: 15 });
  const [previewUrl, setPreviewUrl] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [notice, setNotice] = useState("");

  async function loadNutrition() {
    setNutrition(await getTodayNutrition());
  }

  useEffect(() => {
    loadNutrition();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    await createMeal(form);
    setForm({ ...form, name: "" });
    setAnalysis(null);
    setPreviewUrl("");
    setNotice("Meal saved. AI will update nutrition memory and recommendations.");
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
    setNotice("Review the AI estimate, adjust anything that looks off, then save.");
  }

  return (
    <ProtectedFeaturePage
      title="Nutrition"
      description="Log meals and macros. Each meal writes an event that later feeds memory and adaptive recommendations."
    >
      <div className="grid gap-4 md:grid-cols-3">
        <div className="panel rounded-xl p-4">
          <p className="text-sm text-muted">Calories</p>
          <p className="mt-2 text-3xl font-semibold">{nutrition?.calories ?? 0}</p>
          <p className="text-sm text-muted">of {nutrition?.calorie_target ?? 2200}</p>
        </div>
        <div className="panel rounded-xl p-4">
          <p className="text-sm text-muted">Protein</p>
          <p className="mt-2 text-3xl font-semibold">{nutrition?.protein_g ?? 0}g</p>
          <p className="text-sm text-muted">of {nutrition?.protein_target_g ?? 150}g</p>
        </div>
        <label className="panel flex cursor-pointer flex-col justify-center rounded-xl p-4 transition hover:border-white/20">
          <input type="file" accept="image/*" capture="environment" className="hidden" onChange={handleImageChange} />
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-white p-2 text-slate-950">
              <Camera className="h-4 w-4" />
            </div>
            <div>
              <p className="font-semibold">Analyze meal image</p>
              <p className="text-sm text-muted">Upload, review estimate, then save.</p>
            </div>
          </div>
        </label>
      </div>

      {notice ? <p className="mt-4 text-sm text-limeGlow">{notice}</p> : null}

      {previewUrl ? (
        <section className="mt-5 grid gap-4 rounded-xl border border-white/10 bg-[#0f131d] p-4 md:grid-cols-[220px_1fr]">
          <img src={previewUrl} alt="Uploaded meal preview" className="h-48 w-full rounded-lg object-cover" />
          <div>
            <div className="flex items-center gap-2 text-sm text-muted">
              <Upload className="h-4 w-4" />
              Upload progress {uploadProgress}%
            </div>
            {analysis ? (
              <div className="mt-4 rounded-xl border border-white/10 bg-[#0b0f17] p-3">
                <p className="flex items-center gap-2 text-sm font-semibold">
                  <CheckCircle2 className="h-4 w-4 text-limeGlow" />
                  Editable AI estimate
                </p>
                <p className="mt-2 text-sm text-muted">{analysis.explanation}</p>
                <p className="mt-2 text-xs text-muted">Confidence {Math.round(analysis.confidence * 100)}%</p>
              </div>
            ) : (
              <p className="mt-4 text-sm text-muted">Analyzing meal image locally...</p>
            )}
          </div>
        </section>
      ) : null}

      <form className="mt-5 grid gap-3 rounded-xl border border-white/10 bg-[#0f131d] p-4 md:grid-cols-6" onSubmit={handleSubmit}>
        <Input placeholder="Meal name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
        <Input value={form.meal_type} onChange={(event) => setForm({ ...form, meal_type: event.target.value })} />
        <Input type="number" value={form.calories} onChange={(event) => setForm({ ...form, calories: Number(event.target.value) })} />
        <Input type="number" value={form.protein_g} onChange={(event) => setForm({ ...form, protein_g: Number(event.target.value) })} />
        <Input type="number" value={form.carbs_g} onChange={(event) => setForm({ ...form, carbs_g: Number(event.target.value) })} />
        <Button>Add meal</Button>
      </form>

      <div className="mt-5 space-y-3">
        {(nutrition?.meals || []).map((meal) => (
          <div key={meal.id} className="panel rounded-xl p-4">
            <p className="font-semibold">{meal.name}</p>
            <p className="text-sm text-muted">{meal.calories} kcal - {meal.protein_g}g protein - {meal.carbs_g}g carbs - {meal.fat_g}g fat</p>
            {meal.analysis_explanation ? <p className="mt-2 text-xs text-muted">{meal.analysis_explanation}</p> : null}
          </div>
        ))}
      </div>
    </ProtectedFeaturePage>
  );
}
