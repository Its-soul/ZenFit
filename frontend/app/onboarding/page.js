"use client";

import { ArrowRight, Target } from "lucide-react";
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
    preferred_unit: "metric"
  });
  const [saving, setSaving] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    await completeOnboarding(form);
    router.replace("/dashboard");
  }

  if (loading) {
    return <main className="flex min-h-screen items-center justify-center text-muted">Loading your profile...</main>;
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <form className="glass w-full max-w-2xl rounded-2xl p-8" onSubmit={handleSubmit}>
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyanGlow text-slate-950">
            <Target className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold">Tune your starting plan</h1>
            <p className="text-sm text-muted">These settings become the first facts your AI system uses.</p>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <label>
            <span className="mb-2 block text-sm text-slate-200">Primary goal</span>
            <select
              className="w-full rounded-lg border border-white/15 bg-white/10 px-3 py-2.5 text-sm"
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
            <span className="mb-2 block text-sm text-slate-200">Fitness level</span>
            <select
              className="w-full rounded-lg border border-white/15 bg-white/10 px-3 py-2.5 text-sm"
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
              className="w-full rounded-lg border border-white/15 bg-white/10 px-3 py-2.5 text-sm"
              value={form.preferred_training_days}
              onChange={(event) => setForm({ ...form, preferred_training_days: Number(event.target.value) })}
            >
              {[1, 2, 3, 4, 5, 6, 7].map((day) => (
                <option key={day} value={day}>
                  {day}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span className="mb-2 block text-sm text-slate-200">Units</span>
            <select
              className="w-full rounded-lg border border-white/15 bg-white/10 px-3 py-2.5 text-sm"
              value={form.preferred_unit}
              onChange={(event) => setForm({ ...form, preferred_unit: event.target.value })}
            >
              <option value="metric">Metric</option>
              <option value="imperial">Imperial</option>
            </select>
          </label>
        </div>

        <Button className="mt-8 w-full md:w-auto" disabled={saving}>
          {saving ? "Saving..." : "Enter dashboard"}
          <ArrowRight className="h-4 w-4" />
        </Button>
      </form>
    </main>
  );
}

