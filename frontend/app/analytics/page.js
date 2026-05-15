"use client";

import { useEffect, useState } from "react";

import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { getAnalyticsHistory, getLatestWeeklyReport, getPredictiveAnalytics } from "@/services/analyticsService";

function MiniTrendChart({ title, points, valueKey, maxValue, tone = "bg-cyanGlow" }) {
  const interval = Math.max(1, Math.floor(points.length / 42));
  const sampled = points.filter((_, index) => index % interval === 0);

  return (
    <div className="panel rounded-xl p-4">
      <h2 className="text-sm font-semibold">{title}</h2>
      <div className="mt-4 flex h-28 items-end gap-1">
        {sampled.map((point) => {
          const rawValue = point[valueKey] || 0;
          const height = Math.max(4, Math.round((rawValue / maxValue) * 100));
          return (
            <div
              key={`${point.date}-${valueKey}`}
              className={`w-full rounded-t ${tone}`}
              style={{ height: `${Math.min(height, 100)}%` }}
              title={`${point.date}: ${rawValue}`}
            />
          );
        })}
      </div>
    </div>
  );
}

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [report, setReport] = useState(null);
  const [history, setHistory] = useState(null);

  useEffect(() => {
    async function load() {
      setAnalytics(await getPredictiveAnalytics());
      setReport(await getLatestWeeklyReport());
      setHistory(await getAnalyticsHistory(180));
    }
    load();
  }, []);

  const personalizationItems = analytics?.personalization
    ? [
        ["Coaching style", analytics.personalization.coaching_style?.replaceAll("_", " ") || "Balanced guidance"],
        ["Preferred days", analytics.personalization.preferred_workout_days?.join(", ") || "Still learning"],
        ["Meal rhythm", analytics.personalization.common_meal_hours?.map((hour) => `${hour}:00`).join(", ") || "Still learning"],
        ["Fatigue triggers", analytics.personalization.fatigue_triggers?.join(", ") || "No strong trigger yet"],
        ["Motivation triggers", analytics.personalization.motivation_triggers?.join(", ") || "Still learning"]
      ]
    : [];

  return (
    <ProtectedFeaturePage
      title="Analytics"
      description="Predictive behavior analytics, recovery forecasts, personalization signals, and weekly AI reports."
    >
      <div className="grid gap-4 md:grid-cols-3">
        {Object.entries(analytics?.predictions || {}).map(([key, value]) => (
          <div key={key} className="panel rounded-xl p-4">
            <p className="text-sm capitalize text-muted">{key.replaceAll("_", " ")}</p>
            <p className="mt-2 text-3xl font-semibold">{Math.round(value.score * 100)}%</p>
            <p className="mt-1 text-sm text-muted">Confidence {Math.round(value.confidence * 100)}% - {value.level}</p>
            <p className="mt-3 text-xs text-muted">{value.explanation}</p>
          </div>
        ))}
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-3">
        <MiniTrendChart title="Readiness history" points={history?.points || []} valueKey="readiness_score" maxValue={100} tone="bg-limeGlow" />
        <MiniTrendChart title="Calories logged" points={history?.points || []} valueKey="calories" maxValue={3200} tone="bg-coralGlow" />
        <MiniTrendChart title="Sleep hours" points={history?.points || []} valueKey="sleep_hours" maxValue={9} tone="bg-cyanGlow" />
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <section className="panel rounded-xl p-4">
          <h2 className="font-semibold">Detected trends</h2>
          <div className="mt-4 space-y-3">
            {(analytics?.trends || []).map((trend) => (
              <div key={trend.name} className="soft-panel rounded-xl p-3">
                <p className="text-sm font-semibold">{trend.name}</p>
                <p className="text-sm text-muted">{trend.summary}</p>
              </div>
            ))}
            {!analytics?.trends?.length ? <p className="text-sm text-muted">No strong trends detected yet.</p> : null}
          </div>
        </section>

        <section className="panel rounded-xl p-4">
          <h2 className="font-semibold">Personalization profile</h2>
          <div className="mt-4 space-y-3">
            {personalizationItems.map(([label, value]) => (
              <div key={label} className="soft-panel rounded-xl p-3">
                <p className="text-xs uppercase tracking-wide text-muted">{label}</p>
                <p className="mt-1 text-sm capitalize text-slate-100">{value}</p>
              </div>
            ))}
            {!personalizationItems.length ? <p className="text-sm text-muted">Loading personalization signals...</p> : null}
          </div>
        </section>
      </div>

      <div className="panel mt-5 rounded-xl p-4">
        <h2 className="font-semibold">Weekly AI report</h2>
        <p className="mt-3 text-sm leading-6 text-muted">{report?.summary || "Loading report..."}</p>
      </div>
    </ProtectedFeaturePage>
  );
}
