"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { todayIsoDate } from "@/lib/date";
import { createWorkoutSession, getWorkoutSessions } from "@/services/workoutService";

export default function WorkoutsPage() {
  const [sessions, setSessions] = useState([]);
  const [form, setForm] = useState({
    title: "Strength Session",
    scheduled_date: todayIsoDate(),
    planned_intensity: "moderate",
    duration_minutes: 45,
    notes: ""
  });

  async function loadSessions() {
    setSessions(await getWorkoutSessions());
  }

  useEffect(() => {
    queueMicrotask(loadSessions);
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    await createWorkoutSession(form);
    await loadSessions();
  }

  return (
    <ProtectedFeaturePage
      title="Workouts"
      description="Plan your sessions and keep your week flexible when real life changes."
    >
      <Link href="/workouts/form-check" className="mb-5 inline-flex rounded-xl bg-zenCream px-4 py-2 text-sm font-semibold text-slate-950">Open form checker</Link>
      <form className="grid gap-3 rounded-xl border border-white/10 bg-[#0f131d] p-4 md:grid-cols-5" onSubmit={handleSubmit}>
        <Input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
        <Input type="date" value={form.scheduled_date} onChange={(event) => setForm({ ...form, scheduled_date: event.target.value })} />
        <Input value={form.planned_intensity} onChange={(event) => setForm({ ...form, planned_intensity: event.target.value })} />
        <Input type="number" value={form.duration_minutes} onChange={(event) => setForm({ ...form, duration_minutes: Number(event.target.value) })} />
        <Button>Create</Button>
      </form>

      <div className="mt-5 space-y-3">
        {sessions.map((session) => (
          <div key={session.id} className="panel rounded-xl p-4">
            <div className="flex flex-col justify-between gap-2 md:flex-row md:items-center">
              <div>
                <p className="font-semibold">{session.title}</p>
                <p className="text-sm text-muted">{session.scheduled_date} - {session.duration_minutes} min - {session.planned_intensity}</p>
              </div>
              <span className="rounded-full bg-white/10 px-3 py-1 text-xs">{session.status}</span>
            </div>
          </div>
        ))}
      </div>
    </ProtectedFeaturePage>
  );
}
