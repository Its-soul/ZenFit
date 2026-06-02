"use client";

import { ArrowRight, CheckCircle2, HeartPulse, Target } from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";
import { completeOnboarding } from "@/services/userService";

export default function OnboardingPage() {
  const router = useRouter();
  const { loading } = useAuth({ requireAuth: true });
  const [form, setForm] = useState({
    primary_goal: "Build strength",
    fitness_level: "Beginner",
    preferred_training_days: 4,
    preferred_unit: "metric",
    weight_kg: 70,
    height_cm: 170,
    age: 30,
    biological_sex: "prefer_not_to_say"
  });
  const [struggle, setStruggle] = useState("I miss one day and spiral");
  const [saving, setSaving] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    await completeOnboarding(form);
    router.replace("/dashboard");
  }

  if (loading) {
    return <main className="flex min-h-screen items-center justify-center text-muted">Preparing ZenFit...</main>;
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <form className="panel w-full max-w-4xl rounded-[2rem] p-6 md:p-8" onSubmit={handleSubmit}>
        <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
          <div>
            <div className="mb-8 flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-zenCream text-slate-950">
                <Target className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-semibold text-zenSage">Welcome to ZenFit</p>
                <h1 className="text-3xl font-semibold tracking-[-0.02em]">Let's protect your momentum.</h1>
              </div>
            </div>
            <p className="mb-6 max-w-xl text-sm leading-6 text-muted">
              ZenFit starts by understanding what usually breaks consistency. The first plan is built to survive real life.
            </p>

            <section className="mb-6 rounded-[1.5rem] bg-[#151d16] p-4">
              <p className="flex items-center gap-2 text-sm font-semibold text-zenSage">
                <HeartPulse className="h-4 w-4" />
                What usually breaks your rhythm?
              </p>
              <div className="mt-4 grid gap-2 sm:grid-cols-2">
                {[
                  "I lose motivation",
                  "My schedule changes",
                  "I get tired",
                  "I overthink what to do",
                  "I miss one day and spiral"
                ].map((item) => (
                  <button
                    type="button"
                    key={item}
                    onClick={() => setStruggle(item)}
                    className={`rounded-2xl border px-4 py-3 text-left text-sm transition ${
                      struggle === item ? "border-zenSage bg-zenSage text-[#121711]" : "border-white/10 bg-[#0b0f17] text-slate-200 hover:border-white/25"
                    }`}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </section>

            <div className="grid gap-4 md:grid-cols-2">
              <label>
                <span className="mb-2 block text-sm text-slate-200">Main goal</span>
                <select
                  className="w-full rounded-lg border border-white/10 bg-[#0b0f17] px-3 py-2.5 text-sm"
                  value={form.primary_goal}
                  onChange={(event) => setForm({ ...form, primary_goal: event.target.value })}
                >
                  <option>Build strength</option>
                  <option>Lose fat</option>
                  <option>Improve endurance</option>
                  <option>Build muscle</option>
                  <option>Improve consistency</option>
                </select>
              </label>

              <label>
                <span className="mb-2 block text-sm text-slate-200">Current level</span>
                <select
                  className="w-full rounded-lg border border-white/10 bg-[#0b0f17] px-3 py-2.5 text-sm"
                  value={form.fitness_level}
                  onChange={(event) => setForm({ ...form, fitness_level: event.target.value })}
                >
                  <option>Beginner</option>
                  <option>Intermediate</option>
                  <option>Advanced</option>
                </select>
              </label>

              <label>
                <span className="mb-2 block text-sm text-slate-200">Training days per week</span>
                <select
                  className="w-full rounded-lg border border-white/10 bg-[#0b0f17] px-3 py-2.5 text-sm"
                  value={form.preferred_training_days}
                  onChange={(event) => setForm({ ...form, preferred_training_days: Number(event.target.value) })}
                >
                  {[1, 2, 3, 4, 5, 6, 7].map((day) => (
                    <option key={day} value={day}>{day}</option>
                  ))}
                </select>
              </label>

              <label>
                <span className="mb-2 block text-sm text-slate-200">Units</span>
                <select
                  className="w-full rounded-lg border border-white/10 bg-[#0b0f17] px-3 py-2.5 text-sm"
                  value={form.preferred_unit}
                  onChange={(event) => setForm({ ...form, preferred_unit: event.target.value })}
                >
                  <option value="metric">Metric</option>
                  <option value="imperial">Imperial</option>
                </select>
              </label>

              <label>
                <span className="mb-2 block text-sm text-slate-200">Weight (kg)</span>
                <input
                  className="w-full rounded-lg border border-white/10 bg-[#0b0f17] px-3 py-2.5 text-sm"
                  type="number"
                  min="30"
                  max="300"
                  value={form.weight_kg}
                  onChange={(event) => setForm({ ...form, weight_kg: Number(event.target.value) })}
                />
              </label>

              <label>
                <span className="mb-2 block text-sm text-slate-200">Height (cm)</span>
                <input
                  className="w-full rounded-lg border border-white/10 bg-[#0b0f17] px-3 py-2.5 text-sm"
                  type="number"
                  min="100"
                  max="250"
                  value={form.height_cm}
                  onChange={(event) => setForm({ ...form, height_cm: Number(event.target.value) })}
                />
              </label>

              <label>
                <span className="mb-2 block text-sm text-slate-200">Age</span>
                <input
                  className="w-full rounded-lg border border-white/10 bg-[#0b0f17] px-3 py-2.5 text-sm"
                  type="number"
                  min="13"
                  max="100"
                  value={form.age}
                  onChange={(event) => setForm({ ...form, age: Number(event.target.value) })}
                />
              </label>

              <label>
                <span className="mb-2 block text-sm text-slate-200">Biological sex</span>
                <select
                  className="w-full rounded-lg border border-white/10 bg-[#0b0f17] px-3 py-2.5 text-sm"
                  value={form.biological_sex}
                  onChange={(event) => setForm({ ...form, biological_sex: event.target.value })}
                >
                  <option value="prefer_not_to_say">Prefer not to say</option>
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                  <option value="other">Other</option>
                </select>
              </label>
            </div>

            <Button className="mt-8 w-full md:w-auto" disabled={saving}>
              {saving ? "Creating your plan..." : "Show my Today plan"}
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>

          <aside className="rounded-[1.5rem] bg-zenCream p-5 text-[#121711]">
            <p className="text-sm font-semibold">Your first value moment</p>
            <div className="mt-5 space-y-4">
              {[
                "A workout ready for today",
                "A recovery-aware intensity suggestion",
                "A simple nutrition target",
                "A coach prompt to adjust the plan",
                `A plan that accounts for: ${struggle}`
              ].map((item) => (
                <p key={item} className="flex items-start gap-3 text-sm leading-6">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-green-800" />
                  {item}
                </p>
              ))}
            </div>
          </aside>
        </div>
      </form>
    </main>
  );
}
