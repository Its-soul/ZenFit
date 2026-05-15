"use client";

import { useEffect, useState } from "react";

import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { todayIsoDate } from "@/lib/date";
import { createRecoveryCheckin, getReadiness } from "@/services/recoveryService";

export default function RecoveryPage() {
  const [readiness, setReadiness] = useState(null);
  const [form, setForm] = useState({ checkin_date: todayIsoDate(), fatigue_score: 3, soreness_score: 3, stress_score: 3, notes: "" });

  async function loadReadiness() {
    setReadiness(await getReadiness());
  }

  useEffect(() => {
    loadReadiness();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    await createRecoveryCheckin(form);
    await loadReadiness();
  }

  return (
    <ProtectedFeaturePage
      title="Recovery"
      description="Log fatigue, soreness, and stress. The backend calculates readiness and emits low-readiness events."
    >
      <div className="panel mb-5 rounded-xl p-4">
        <p className="text-sm text-muted">Latest readiness</p>
        <p className="mt-2 text-4xl font-semibold">{readiness?.readiness_score ?? "--"}</p>
      </div>

      <form className="grid gap-3 rounded-xl border border-white/10 bg-[#0f131d] p-4 md:grid-cols-6" onSubmit={handleSubmit}>
        <Input type="date" max={todayIsoDate()} value={form.checkin_date} onChange={(event) => setForm({ ...form, checkin_date: event.target.value })} />
        <Input type="number" value={form.fatigue_score} onChange={(event) => setForm({ ...form, fatigue_score: Number(event.target.value) })} />
        <Input type="number" value={form.soreness_score} onChange={(event) => setForm({ ...form, soreness_score: Number(event.target.value) })} />
        <Input type="number" value={form.stress_score} onChange={(event) => setForm({ ...form, stress_score: Number(event.target.value) })} />
        <Input placeholder="Notes" value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
        <Button>Save</Button>
      </form>
    </ProtectedFeaturePage>
  );
}
