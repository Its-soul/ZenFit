"use client";

import { CalendarCheck, HeartPulse, Moon, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";

import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { getAnalyticsHistory, getLatestWeeklyReport, getPredictiveAnalytics } from "@/services/analyticsService";

function MiniTrendChart({ title, points, valueKey, maxValue, tone = "bg-zenSage" }) {
  const interval = Math.max(1, Math.floor(points.length / 42));
  const sampled = points.filter((_, index) => index % interval === 0);

  return (
    <div className="panel rounded-xl p-4">
      <h2 className="text-sm font-semibold">{title}</h2>
      <div className="mt-4 flex h-28 items-end gap-1">
        {sampled.map((point) => {
          const rawValue = point[valueKey] || 0;
          const height = Math.max(4, Math.round((rawValue / maxValue) * 100));
          return <div key={`${point.date}-${valueKey}`} className={`w-full rounded-t ${tone}`} style={{ height: `${Math.min(height, 100)}%` }} />;
        })}
      </div>
    </div>
  );
}

function progressCards(analytics) {
  const predictions = analytics?.predictions || {};
  return [
    {
      title: "Consistency outlook",
      value: predictions.workout_completion_probability ? `${Math.round(predictions.workout_completion_probability.score * 100)}%` : "Building",
      helper: "Chance you keep momentum this week",
      icon: CalendarCheck
    },
    {
      title: "Recovery balance",
      value: predictions.recovery_decline?.level ? predictions.recovery_decline.level : "Steady",
      helper: "How your body is handling training",
      icon: HeartPulse
    },
    {
      title: "Nutrition rhythm",
      value: predictions.calorie_adherence_consistency ? `${Math.round(predictions.calorie_adherence_consistency.score * 100)}%` : "Learning",
      helper: "How consistent meal logging feels",
      icon: TrendingUp
    }
  ];
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

  return (
    <ProtectedFeaturePage
      title="Progress"
      description="A simple view of what is improving, what needs care, and what to focus on next."
    >
      <div className="grid gap-4 md:grid-cols-3">
        {progressCards(analytics).map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.title} className="panel rounded-xl p-4">
              <Icon className="h-5 w-5 text-zenSage" />
              <p className="mt-4 text-sm text-muted">{item.title}</p>
              <p className="mt-2 text-3xl font-semibold capitalize">{item.value}</p>
              <p className="mt-2 text-sm text-muted">{item.helper}</p>
            </div>
          );
        })}
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-3">
        <MiniTrendChart title="Recovery trend" points={history?.points || []} valueKey="readiness_score" maxValue={100} tone="bg-zenSage" />
        <MiniTrendChart title="Meal energy" points={history?.points || []} valueKey="calories" maxValue={3200} tone="bg-zenGold" />
        <MiniTrendChart title="Sleep rhythm" points={history?.points || []} valueKey="sleep_hours" maxValue={9} tone="bg-coralGlow" />
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <section className="panel rounded-xl p-4">
          <h2 className="flex items-center gap-2 font-semibold">
            <TrendingUp className="h-4 w-4 text-zenSage" />
            Helpful patterns
          </h2>
          <div className="mt-4 space-y-3">
            {(analytics?.trends || []).map((trend) => (
              <div key={trend.name} className="soft-panel rounded-xl p-3">
                <p className="text-sm font-semibold">{trend.name}</p>
                <p className="text-sm leading-6 text-muted">{trend.summary}</p>
              </div>
            ))}
            {!analytics?.trends?.length ? <p className="text-sm text-muted">ZenFit is still learning your rhythm.</p> : null}
          </div>
        </section>

        <section className="panel rounded-xl p-4">
          <h2 className="flex items-center gap-2 font-semibold">
            <Moon className="h-4 w-4 text-zenSage" />
            Weekly reflection
          </h2>
          <p className="mt-4 text-sm leading-6 text-muted">{report?.summary || "Your weekly reflection will appear after more activity."}</p>
        </section>
      </div>
    </ProtectedFeaturePage>
  );
}
