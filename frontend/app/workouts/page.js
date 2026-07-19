"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Field } from "@/components/ui/Field";
import { Select } from "@/components/ui/Select";
import { todayIsoDate } from "@/lib/date";
import { createWorkoutSession, getWorkoutSessions } from "@/services/workoutService";

export default function WorkoutsPage() {
  const [sessions, setSessions] = useState([]);
  const [form, setForm] = useState({
    title: "Strength Session",
    scheduled_date: todayIsoDate(),
    planned_intensity: "moderate",
    duration_minutes: "45",
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
    await createWorkoutSession({ ...form, duration_minutes: Number(form.duration_minutes) });
    await loadSessions();
  }

  return (
    <ProtectedFeaturePage
      title="Workouts"
      description="Plan your sessions and keep your week flexible when real life changes."
    >
      <Link href="/workouts/form-check" className="mb-5 inline-flex rounded-xl bg-zenCream px-4 py-2 text-sm font-semibold text-slate-950">Open form checker</Link>
      <form className="soft-panel grid gap-4 rounded-[var(--radius-md)] p-4 sm:grid-cols-2 xl:grid-cols-4" onSubmit={handleSubmit}>
        <Field label="Session name"><Input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} /></Field>
        <Field label="Training date"><Input type="date" value={form.scheduled_date} onChange={(event) => setForm({ ...form, scheduled_date: event.target.value })} /></Field>
        <Field label="Planned intensity"><Select value={form.planned_intensity} onChange={(event) => setForm({ ...form, planned_intensity: event.target.value })}><option value="light">Light</option><option value="moderate">Moderate</option><option value="hard">Hard</option></Select></Field>
        <Field label="Duration in minutes"><Input inputMode="numeric" value={form.duration_minutes} onChange={(event) => /^\d*$/.test(event.target.value) && setForm({ ...form, duration_minutes: event.target.value })} /></Field>
        <Button className="sm:col-span-2 sm:justify-self-start xl:col-span-4">Add to my week</Button>
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
