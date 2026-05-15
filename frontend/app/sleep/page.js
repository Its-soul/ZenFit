"use client";

import { useEffect, useState } from "react";

import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { todayIsoDate } from "@/lib/date";
import { createSleepLog, getSleepLogs } from "@/services/sleepService";

export default function SleepPage() {
  const [logs, setLogs] = useState([]);
  const [form, setForm] = useState({ sleep_date: todayIsoDate(), duration_hours: 7.5, quality_score: 80, notes: "" });

  async function loadLogs() {
    setLogs(await getSleepLogs());
  }

  useEffect(() => {
    loadLogs();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    await createSleepLog(form);
    await loadLogs();
  }

  return (
    <ProtectedFeaturePage
      title="Sleep"
      description="Sleep logs influence readiness and trigger poor-sleep events when recovery risk rises."
    >
      <form className="grid gap-3 rounded-xl border border-white/10 bg-[#0f131d] p-4 md:grid-cols-5" onSubmit={handleSubmit}>
        <Input type="date" max={todayIsoDate()} value={form.sleep_date} onChange={(event) => setForm({ ...form, sleep_date: event.target.value })} />
        <Input type="number" step="0.25" value={form.duration_hours} onChange={(event) => setForm({ ...form, duration_hours: Number(event.target.value) })} />
        <Input type="number" value={form.quality_score} onChange={(event) => setForm({ ...form, quality_score: Number(event.target.value) })} />
        <Input placeholder="Notes" value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
        <Button>Save sleep</Button>
      </form>

      <div className="mt-5 space-y-3">
        {logs.map((log) => (
          <div key={log.id} className="panel rounded-xl p-4">
            <p className="font-semibold">{log.duration_hours} hours</p>
            <p className="text-sm text-muted">{log.sleep_date} - quality {log.quality_score}/100</p>
          </div>
        ))}
      </div>
    </ProtectedFeaturePage>
  );
}
