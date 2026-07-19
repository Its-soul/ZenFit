"use client";

import { ArrowRight, CheckCircle2, HeartPulse, Target } from "lucide-react";
import { memo, useCallback, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/Button";
import NumericTextField from "./NumericTextField";
import { getApiErrorMessage } from "@/services/apiClient";
import { completeOnboarding } from "@/services/userService";

const struggles = ["I lose motivation", "My schedule changes", "I get tired", "I overthink what to do", "I miss one day and spiral"];
const numericRules = {
  weight_kg: { label: "Weight", min: 30, max: 300 },
  height_cm: { label: "Height", min: 100, max: 250 },
  age: { label: "Age", min: 13, max: 100, integer: true }
};

const ValueSummary = memo(function ValueSummary({ struggle }) {
  const values = ["A workout ready for today", "A recovery-aware intensity suggestion", "A simple nutrition target", "A coach prompt to adjust the plan", `A plan that accounts for: ${struggle}`];
  return (
    <aside className="min-w-0 self-start rounded-[1.5rem] bg-zenCream p-[clamp(1.25rem,3vw,1.5rem)] text-[#121711] lg:sticky lg:top-8">
      <p className="text-sm font-semibold text-green-800">What you&apos;ll get first</p>
      <h2 className="mt-2 text-2xl font-semibold leading-8">A plan that already feels possible.</h2>
      <p className="mt-2 text-sm leading-6 text-slate-600">Your answers shape today&apos;s guidance. They are not a score.</p>
      <div className="mt-5 space-y-4">
        {values.map((item) => <p key={item} className="flex items-start gap-3 break-words text-sm leading-6"><CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-green-800" />{item}</p>)}
      </div>
    </aside>
  );
});

function validateNumeric(field, value) {
  const rule = numericRules[field];
  if (!value.trim()) return `Add your ${rule.label.toLowerCase()} so we can personalize your plan.`;
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return `Enter your ${rule.label.toLowerCase()} as a number so we can personalize your plan.`;
  if (rule.integer && !Number.isInteger(parsed)) return `Enter your ${rule.label.toLowerCase()} as a whole number.`;
  if (parsed < rule.min || parsed > rule.max) return `Enter a ${rule.label.toLowerCase()} between ${rule.min} and ${rule.max} so we can personalize your plan.`;
  return "";
}

export default function OnboardingForm() {
  const router = useRouter();
  const initialForm = { primary_goal: "Build strength", fitness_level: "Beginner", preferred_training_days: "4", preferred_unit: "metric", weight_kg: "70", height_cm: "170", age: "30", biological_sex: "prefer_not_to_say" };
  const [form, setForm] = useState(initialForm);
  const formRef = useRef(initialForm);
  const [struggle, setStruggle] = useState("I miss one day and spiral");
  const [fieldErrors, setFieldErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const updateNumeric = useCallback((field, nextValue, integer) => {
    const allowed = integer ? /^\d*$/ : /^\d*(?:\.\d*)?$/;
    if (!allowed.test(nextValue)) return;
    setForm((current) => {
      const next = { ...current, [field]: nextValue };
      formRef.current = next;
      return next;
    });
    setFieldErrors((current) => current[field] ? { ...current, [field]: "" } : current);
  }, []);

  const normalizeNumeric = useCallback((field) => {
    const current = formRef.current;
    const message = validateNumeric(field, current[field]);
    setFieldErrors((errors) => ({ ...errors, [field]: message }));
    if (message || current[field] === "") return;
    const next = { ...current, [field]: String(Number(current[field])) };
    formRef.current = next;
    setForm(next);
  }, []);

  function updateField(field, value) {
    setForm((current) => {
      const next = { ...current, [field]: value };
      formRef.current = next;
      return next;
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (saving) return;
    const errors = Object.fromEntries(Object.keys(numericRules).map((field) => [field, validateNumeric(field, form[field])]));
    setFieldErrors(errors);
    if (Object.values(errors).some(Boolean)) return;
    setError("");
    setSaving(true);
    try {
      await completeOnboarding({ ...form, preferred_training_days: Number(form.preferred_training_days), weight_kg: Number(form.weight_kg), height_cm: Number(form.height_cm), age: Number(form.age) });
      router.replace("/dashboard");
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "We could not save onboarding. Try again."));
    } finally {
      setSaving(false);
    }
  }

  const controlClass = "w-full rounded-lg border border-white/10 bg-[#0b0f17] px-3 py-2.5 text-sm text-white outline-none transition-[border-color,box-shadow] focus-visible:border-zenSage focus-visible:ring-2 focus-visible:ring-zenSage/20";
  return (
    <form className="panel w-full max-w-5xl overflow-hidden rounded-[clamp(1.25rem,3vw,2rem)] p-[clamp(1.25rem,3vw,2rem)]" onSubmit={handleSubmit} noValidate>
      <div className="grid min-w-0 gap-8 lg:grid-cols-[minmax(0,1fr)_minmax(16rem,20rem)] xl:gap-10">
        <div className="min-w-0">
          <div className="mb-7 flex items-start gap-3">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-zenCream text-slate-950"><Target className="h-5 w-5" /></div>
            <div className="min-w-0"><p className="text-sm font-semibold text-zenSage">Welcome to ZenFit</p><h1 className="text-[clamp(1.75rem,5vw,2.25rem)] font-semibold leading-tight tracking-[-0.02em]">Let&apos;s protect your momentum.</h1></div>
          </div>
          <p className="mb-6 max-w-xl text-sm leading-6 text-muted">ZenFit starts by understanding what usually breaks consistency. The first plan is built to survive real life.</p>
          <section className="mb-6 rounded-[1.5rem] border border-zenSage/10 bg-[#151d16] p-[clamp(1rem,3vw,1.25rem)]" aria-labelledby="rhythm-label">
            <p id="rhythm-label" className="flex items-center gap-2 text-sm font-semibold text-zenSage"><HeartPulse className="h-4 w-4" />What usually breaks your rhythm?</p>
            <p className="mt-2 text-sm leading-6 text-muted">There is no wrong answer. This helps your plan bend when life changes.</p>
            <div className="mt-4 grid gap-2 sm:grid-cols-2">
              {struggles.map((item) => <button type="button" key={item} aria-pressed={struggle === item} onClick={() => setStruggle(item)} className={`rounded-2xl border px-4 py-3 text-left text-sm outline-none transition-[background-color,border-color,color] focus-visible:ring-2 focus-visible:ring-zenSage ${struggle === item ? "border-zenSage bg-zenSage font-semibold text-[#121711] shadow-[0_0_0_1px_rgba(143,232,197,0.35)]" : "border-white/10 bg-[#0b0f17] text-slate-200 hover:border-white/25"}`}>{item}</button>)}
            </div>
          </section>
          <div className="grid min-w-0 gap-4 sm:grid-cols-2">
            <label><span className="mb-2 block text-sm text-slate-200">Main goal</span><select className={controlClass} value={form.primary_goal} onChange={(event) => updateField("primary_goal", event.target.value)}><option>Build strength</option><option>Lose fat</option><option>Improve endurance</option><option>Build muscle</option><option>Improve consistency</option></select></label>
            <label><span className="mb-2 block text-sm text-slate-200">Current level</span><select className={controlClass} value={form.fitness_level} onChange={(event) => updateField("fitness_level", event.target.value)}><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></label>
            <label><span className="mb-2 block text-sm text-slate-200">Training days per week</span><select className={controlClass} value={form.preferred_training_days} onChange={(event) => updateField("preferred_training_days", event.target.value)}>{[1,2,3,4,5,6,7].map((day) => <option key={day} value={day}>{day}</option>)}</select></label>
            <label><span className="mb-2 block text-sm text-slate-200">Units</span><select className={controlClass} value={form.preferred_unit} onChange={(event) => updateField("preferred_unit", event.target.value)}><option value="metric">Metric</option><option value="imperial">Imperial</option></select></label>
            <NumericTextField field="weight_kg" label="Weight (kg)" value={form.weight_kg} error={fieldErrors.weight_kg} onChange={updateNumeric} onBlur={normalizeNumeric} />
            <NumericTextField field="height_cm" label="Height (cm)" value={form.height_cm} error={fieldErrors.height_cm} onChange={updateNumeric} onBlur={normalizeNumeric} />
            <NumericTextField field="age" label="Age" value={form.age} error={fieldErrors.age} integer onChange={updateNumeric} onBlur={normalizeNumeric} />
            <label><span className="mb-2 block text-sm text-slate-200">Biological sex</span><select className={controlClass} value={form.biological_sex} onChange={(event) => updateField("biological_sex", event.target.value)}><option value="prefer_not_to_say">Prefer not to say</option><option value="female">Female</option><option value="male">Male</option><option value="other">Other</option></select></label>
          </div>
          <Button className="mt-8 w-full sm:w-auto" disabled={saving} aria-busy={saving}>{saving ? "Creating your plan..." : "Show my Today plan"}<ArrowRight className="h-4 w-4" /></Button>
          {error ? <p role="alert" className="mt-4 rounded-lg border border-red-400/30 bg-red-500/10 px-3 py-2 text-sm text-red-100">{error}</p> : null}
        </div>
        <ValueSummary struggle={struggle} />
      </div>
    </form>
  );
}
