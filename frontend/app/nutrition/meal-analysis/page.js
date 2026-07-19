"use client";

import { Camera, Check, ImageUp, LoaderCircle, Plus, Trash2 } from "lucide-react";
import Image from "next/image";
import { useEffect, useMemo, useState } from "react";

import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { getApiErrorMessage } from "@/services/apiClient";
import { getAiHealth } from "@/services/aiService";
import { analyzeMealImageLocal, confirmMealAnalysis, createMeal, lookupMeal } from "@/services/nutritionService";

const blankFood = () => ({ name: "", quantity: "1", grams: "100", nutrition: {}, baseGrams: 100, confidence_level: "low", top_candidates: [] });

function ManualFoodRow({ food, index, onEdit, onRemove }) {
  return (
    <div className="rounded-xl border border-white/10 p-3">
      <div className="grid min-w-0 gap-3 sm:grid-cols-2 xl:grid-cols-[minmax(0,1fr)_7rem_7rem_2.5rem] xl:items-end">
        <label className="min-w-0"><span className="mb-1.5 block text-xs font-medium text-slate-300">Food name</span><Input value={food.name} placeholder="e.g. chicken breast" onChange={(event) => onEdit(index, "name", event.target.value)} /></label>
        <label className="min-w-0"><span className="mb-1.5 block text-xs font-medium text-slate-300">Quantity / pieces</span><Input inputMode="decimal" value={food.quantity} placeholder="1" onChange={(event) => onEdit(index, "quantity", event.target.value)} /></label>
        <label className="min-w-0"><span className="mb-1.5 block text-xs font-medium text-slate-300">Total grams</span><Input inputMode="decimal" value={food.grams} placeholder="100" onChange={(event) => onEdit(index, "grams", event.target.value)} /></label>
        <button type="button" aria-label={`Remove ${food.name || `food ${index + 1}`}`} onClick={() => onRemove(index)} className="inline-flex h-10 w-full items-center justify-center rounded-lg text-muted outline-none transition-colors hover:bg-white/10 hover:text-white focus-visible:ring-2 focus-visible:ring-zenSage sm:col-span-2 xl:col-span-1 xl:w-10"><Trash2 className="h-4 w-4" /></button>
      </div>
      {food.food_confidence ? <p className="mt-2 text-xs text-muted">Recognition confidence: <span className={food.confidence_level === "high" ? "text-zenSage" : food.confidence_level === "medium" ? "text-amber-200" : "text-coralGlow"}>{food.confidence_level}</span> · Portion confidence: {Math.round((food.portion_confidence || 0) * 100)}%</p> : null}
    </div>
  );
}

export default function MealAnalysisPage() {
  const [capability, setCapability] = useState("checking");
  const [statusNotice, setStatusNotice] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [foods, setFoods] = useState([blankFood()]);
  const [manualEstimate, setManualEstimate] = useState(null);
  const [stage, setStage] = useState("");
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [trainingConsent, setTrainingConsent] = useState(false);

  useEffect(() => {
    let active = true;
    getAiHealth().then((result) => {
      if (!active) return;
      const next = result?.meal_scan?.overall || "unavailable";
      setCapability(next);
      if (next === "unavailable") setStatusNotice("Automatic recognition is currently unavailable. Upload preview and manual meal entry remain available.");
      else if (next === "partial") setStatusNotice("Automatic recognition is limited. Review every detected food and portion before saving.");
    }).catch(() => {
      if (!active) return;
      setCapability("unavailable");
      setStatusNotice("Meal scanning status is unavailable. Upload preview and manual meal entry remain available.");
    });
    return () => { active = false; };
  }, []);

  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);

  function choose(event) {
    const next = event.target.files?.[0];
    if (!next) return;
    setFile(next);
    setPreview(URL.createObjectURL(next));
    setAnalysis(null);
    setError("");
    setSaved(false);
  }

  async function analyze() {
    if (!file || capability === "unavailable" || capability === "checking" || stage) return;
    setStage("Analyzing meal...");
    setError("");
    try {
      const result = await analyzeMealImageLocal(file);
      setAnalysis(result);
      setManualEstimate(null);
      setFoods(result.foods.length ? result.foods.map((food) => ({ ...food, quantity: String(food.quantity ?? 1), grams: String(food.estimated_grams ?? ""), baseGrams: food.estimated_grams || 1 })) : [blankFood()]);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "We couldn't analyze this image. Continue with manual food entry."));
    } finally {
      setStage("");
    }
  }

  function edit(index, key, value) {
    if (key !== "name" && !/^\d*(?:\.\d*)?$/.test(value)) return;
    setFoods((items) => items.map((item, itemIndex) => itemIndex === index ? { ...item, [key]: value } : item));
    setManualEstimate(null);
    setSaved(false);
  }

  function validFoods() {
    const clean = foods.map((food) => ({ name: food.name.trim(), quantity: Number(food.quantity), grams: Number(food.grams) }));
    if (!clean.length || clean.some((food) => !food.name || !Number.isFinite(food.quantity) || food.quantity <= 0 || !Number.isFinite(food.grams) || food.grams <= 0)) {
      setError("Enter a food name, positive quantity, and positive gram amount for every row.");
      return null;
    }
    return clean;
  }

  async function calculateManualNutrition(cleanFoods) {
    const response = await lookupMeal(cleanFoods.map((food) => `${food.grams}g ${food.name}`).join(", "));
    setManualEstimate(response);
    return response;
  }

  async function updateTotals() {
    if (stage) return;
    const clean = validFoods();
    if (!clean) return;
    setStage("Updating nutrition...");
    setError("");
    try { await calculateManualNutrition(clean); }
    catch (requestError) { setError(getApiErrorMessage(requestError, "Nutrition totals could not be calculated. Check the food names and try again.")); }
    finally { setStage(""); }
  }

  async function confirm() {
    if (stage || saved) return;
    const clean = validFoods();
    if (!clean) return;
    setStage("Saving meal...");
    setError("");
    try {
      if (analysis) {
        await confirmMealAnalysis({ analysis_id: analysis.analysis_id, foods: clean, training_consent: trainingConsent });
      } else {
        const nutrition = manualEstimate || await calculateManualNutrition(clean);
        await createMeal(nutrition.estimate);
      }
      setSaved(true);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "The meal could not be saved. Please review the entries and try again."));
    } finally {
      setStage("");
    }
  }

  const totals = useMemo(() => {
    if (!analysis && manualEstimate) return { calories: manualEstimate.total_calories || 0, protein_g: manualEstimate.protein_g || 0, carbs_g: manualEstimate.carbs_g || 0, fat_g: manualEstimate.fat_g || 0, fiber_g: 0 };
    return ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g"].reduce((result, key) => ({ ...result, [key]: foods.reduce((sum, food) => sum + (Number(food.nutrition?.[key]) || 0) * (Number(food.grams) || 0) / (food.baseGrams || Number(food.grams) || 1), 0) }), {});
  }, [analysis, foods, manualEstimate]);

  const scanDisabled = !file || capability === "unavailable" || capability === "checking" || Boolean(stage);
  return (
    <ProtectedFeaturePage title="Meal analysis" description="Upload a meal photo, review every estimate, and correct portions before saving.">
      {statusNotice ? <div role="status" className="mb-5 rounded-xl border border-amber-300/20 bg-amber-400/10 p-3 text-sm leading-6 text-amber-100">{statusNotice}</div> : null}
      <div className="grid min-w-0 gap-5 xl:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
        <section className="panel min-w-0 rounded-2xl p-[clamp(1rem,3vw,1.25rem)]">
          <div className="flex items-center gap-2"><Camera className="h-5 w-5 text-zenSage" /><h2 className="font-semibold">Meal photo</h2></div>
          <label className="mt-4 flex min-h-52 cursor-pointer items-center justify-center overflow-hidden rounded-2xl border border-dashed border-white/20 bg-black/20 outline-none focus-within:border-zenSage focus-within:ring-2 focus-within:ring-zenSage/20 sm:min-h-64">
            {preview ? <Image unoptimized width={800} height={600} src={preview} alt="Uploaded meal preview" className="max-h-80 w-full object-contain" /> : <span className="flex flex-col items-center gap-2 px-4 text-center text-sm text-muted"><ImageUp />Choose or capture a JPEG, PNG, or WebP image</span>}
            <input className="sr-only" type="file" accept="image/jpeg,image/png,image/webp" capture="environment" onChange={choose} />
          </label>
          <Button type="button" className="mt-4 w-full" disabled={scanDisabled} onClick={analyze} aria-describedby={capability === "unavailable" ? "scan-unavailable" : undefined}>{stage === "Analyzing meal..." ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <ImageUp className="h-4 w-4" />}{capability === "checking" ? "Checking availability..." : capability === "unavailable" ? "Analyze meal unavailable" : stage === "Analyzing meal..." ? stage : "Analyze meal"}</Button>
          {capability === "unavailable" ? <p id="scan-unavailable" className="mt-2 text-xs leading-5 text-muted">Add foods manually in the review panel. No image-analysis request will be sent.</p> : null}
        </section>

        <section className="panel min-w-0 rounded-2xl p-[clamp(1rem,3vw,1.25rem)]">
          <h2 className="font-semibold">Review foods</h2><p className="mt-1 text-sm leading-6 text-muted">Enter each food, its quantity or pieces, and the total gram amount.</p>
          {analysis?.recognition_message && analysis.recognition_decision !== "MODEL_UNAVAILABLE" ? <p className="mt-3 rounded-xl bg-white/5 p-3 text-sm text-muted">{analysis.recognition_message}</p> : null}
          <div className="mt-4 space-y-3">{foods.map((food, index) => <ManualFoodRow key={index} food={food} index={index} onEdit={edit} onRemove={(itemIndex) => { setFoods((items) => items.filter((_, index) => index !== itemIndex)); setManualEstimate(null); }} />)}</div>
          <div className="mt-3 flex flex-wrap gap-2"><Button type="button" variant="secondary" onClick={() => { setFoods((items) => [...items, blankFood()]); setManualEstimate(null); }}><Plus className="h-4 w-4" />Add food</Button><Button type="button" variant="secondary" disabled={!foods.length || Boolean(stage)} onClick={updateTotals}>{stage === "Updating nutrition..." ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}{stage === "Updating nutrition..." ? stage : "Update nutrition totals"}</Button></div>
          <div className="mt-4 grid grid-cols-2 gap-2 rounded-xl bg-white/5 p-3 text-sm sm:grid-cols-3 xl:grid-cols-5"><span>{Math.round(totals.calories)} kcal</span><span>{Number(totals.protein_g).toFixed(1)}g protein</span><span>{Number(totals.carbs_g).toFixed(1)}g carbs</span><span>{Number(totals.fat_g).toFixed(1)}g fat</span><span>{Number(totals.fiber_g).toFixed(1)}g fiber</span></div>
          {manualEstimate?.warnings?.length ? <p className="mt-3 rounded-xl bg-white/5 p-3 text-sm text-muted">{manualEstimate.warnings.join(" ")}</p> : null}
          {error ? <p role="alert" className="mt-4 rounded-xl border border-red-400/20 bg-red-500/10 p-3 text-sm text-coralGlow">{error}</p> : null}
          {saved ? <p className="mt-4 flex items-center gap-2 text-sm text-zenSage"><Check className="h-4 w-4" />Meal saved and today&apos;s totals were updated.</p> : null}
          <label className="mt-5 flex items-start gap-3 rounded-xl bg-white/5 p-3 text-xs leading-5 text-muted"><input className="mt-0.5 h-4 w-4 shrink-0 accent-[#8FE8C5]" type="checkbox" checked={trainingConsent} onChange={(event) => setTrainingConsent(event.target.checked)} /><span>Allow this meal image to be considered for future anonymized recognition improvement. Off by default; current implementation records consent but does not retain the image for training.</span></label>
          <Button type="button" className="mt-4 w-full" disabled={!foods.length || Boolean(stage) || saved} onClick={confirm} aria-busy={stage === "Saving meal..."}>{stage === "Saving meal..." ? <LoaderCircle className="h-4 w-4 animate-spin" /> : null}{stage === "Saving meal..." ? stage : "Confirm and save meal"}</Button>
        </section>
      </div>
    </ProtectedFeaturePage>
  );
}
