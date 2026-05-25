"use client";

import { Moon, Sunrise } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { RecoveryStoryCard } from "@/components/product/RecoveryStoryCard";
import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { todayIsoDate } from "@/lib/date";
import { createSleepLog, getSleepLogs } from "@/services/sleepService";

function sleepStory(logs) {
  const recent = logs.slice(0, 5);
  const latest = recent[0];
  const lowNights = recent.filter((log) => log.duration_hours < 6.5 || log.quality_score < 60).length;

  if (!latest) {
    return {
      title: "Sleep is the fastest recovery signal.",
      cause: "ZenFit has not seen last night's sleep yet.",
      effect: "Today’s training intensity is easier to adjust after one sleep log.",
      recommendation: "Log last night. Keep it approximate.",
      icon: "sleep"
    };
  }

  if (lowNights >= 2) {
    return {
      title: "Recovery dropped after low-sleep nights.",
      cause: `${lowNights} of your recent nights were short or low quality.`,
      effect: "Training may feel heavier and motivation may dip faster.",
      recommendation: "Protect momentum with lighter movement and an earlier wind-down tonight.",
      tone: "coral",
      icon: "sleep"
    };
  }

  if (latest.duration_hours >= 7.5 && latest.quality_score >= 75) {
    return {
      title: "Sleep is supporting your training.",
      cause: "Your latest sleep log gives your body a stronger recovery base.",
      effect: "You are more likely to handle the planned session well.",
      recommendation: "Use the good recovery, then repeat the bedtime rhythm.",
      tone: "gold",
      icon: "sleep"
    };
  }

  return {
    title: "Sleep is steady enough to build from.",
    cause: "Your latest sleep was not perfect, but it is usable.",
    effect: "A normal session can work if the warm-up feels good.",
    recommendation: "Train steady, then make tonight's wind-down the next win.",
    icon: "sleep"
  };
}

export default function SleepPage() {
  const [logs, setLogs] = useState([]);
  const [form, setForm] = useState({ sleep_date: todayIsoDate(), duration_hours: 7.5, quality_score: 80, notes: "" });
  const [notice, setNotice] = useState("");

  async function loadLogs() {
    setLogs(await getSleepLogs());
  }

  useEffect(() => {
    loadLogs();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    await createSleepLog(form);
    setNotice("Sleep saved. ZenFit can now tune today around your recovery.");
    await loadLogs();
  }

  const story = useMemo(() => sleepStory(logs), [logs]);

  return (
    <ProtectedFeaturePage
      title="Sleep"
      description="Turn rest into better training decisions, not another score to worry about."
    >
      {notice ? <p className="mb-4 text-sm text-zenSage">{notice}</p> : null}
      <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <RecoveryStoryCard {...story} />
        <section className="panel rounded-[1.5rem] p-6">
          <Moon className="h-5 w-5 text-zenSage" />
          <h2 className="mt-4 text-2xl font-semibold">Log last night</h2>
          <p className="mt-2 text-sm text-muted">Approximate is enough. The goal is better guidance, not perfect tracking.</p>
          <form className="mt-5 grid gap-3" onSubmit={handleSubmit}>
            <Input type="date" max={todayIsoDate()} value={form.sleep_date} onChange={(event) => setForm({ ...form, sleep_date: event.target.value })} />
            <Input type="number" step="0.25" value={form.duration_hours} onChange={(event) => setForm({ ...form, duration_hours: Number(event.target.value) })} placeholder="Hours slept" />
            <Input type="number" value={form.quality_score} onChange={(event) => setForm({ ...form, quality_score: Number(event.target.value) })} placeholder="Quality 1-100" />
            <Input placeholder="What affected sleep?" value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} />
            <Button>
              <Sunrise className="h-4 w-4" />
              Save sleep
            </Button>
          </form>
        </section>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2">
        {logs.slice(0, 6).map((log) => (
          <div key={log.id} className="panel rounded-2xl p-4">
            <p className="font-semibold">{log.duration_hours} hours</p>
            <p className="mt-1 text-sm text-muted">{log.sleep_date} / quality {log.quality_score}/100</p>
            <p className="mt-2 text-sm text-muted">
              {log.duration_hours >= 7 ? "This supports tomorrow's recovery." : "A lighter training day may help protect momentum."}
            </p>
          </div>
        ))}
      </div>
    </ProtectedFeaturePage>
  );
}
