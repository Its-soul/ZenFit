"use client";

import { Activity, Brain, CalendarClock, CheckCircle2, Flame, Moon, Radio, Salad, Sparkles, XCircle } from "lucide-react";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { GlassPanel } from "@/components/common/GlassPanel";
import { MetricCard } from "@/components/common/MetricCard";
import { useAuth } from "@/hooks/useAuth";
import { useRealtimeDashboard } from "@/hooks/useRealtimeDashboard";
import { getTodayDashboard } from "@/services/dashboardService";
import { sendRecommendationFeedback } from "@/services/recommendationService";
import { completeWorkoutSession, missWorkoutSession, rescheduleWorkoutSession } from "@/services/workoutService";
import { Button } from "@/components/ui/Button";

export default function DashboardPage() {
  const { user, loading, logout } = useAuth({ requireAuth: true });
  const realtime = useRealtimeDashboard();
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [rescheduleDate, setRescheduleDate] = useState("");

  async function loadDashboard() {
    try {
      setDashboard(await getTodayDashboard());
      setError("");
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to load dashboard");
    }
  }

  useEffect(() => {
    if (!loading) loadDashboard();
  }, [loading]);

  useEffect(() => {
    if (realtime.lastMessage?.type === "ai.event.processed") {
      const source = realtime.lastMessage.payload?.source_event?.replaceAll(".", " ");
      setNotice(source ? `AI updated your plan after ${source}.` : "AI updated your dashboard.");
      loadDashboard();
    }
  }, [realtime.lastMessage]);

  async function updateWorkout(action) {
    if (!dashboard?.today_workout?.id) return;
    try {
      if (action === "complete") {
        await completeWorkoutSession(dashboard.today_workout.id);
        setNotice("Workout marked complete.");
      } else {
        await missWorkoutSession(dashboard.today_workout.id);
        setNotice("Workout marked missed. AI will adapt the plan.");
      }
      await loadDashboard();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to update workout");
    }
  }

  async function rescheduleWorkout() {
    if (!dashboard?.today_workout?.id || !rescheduleDate) return;
    try {
      await rescheduleWorkoutSession(dashboard.today_workout.id, {
        scheduled_date: rescheduleDate,
        reason: "User moved this workout from the dashboard"
      });
      setNotice("Workout rescheduled. Your dashboard will update when AI finishes processing.");
      setRescheduleDate("");
      await loadDashboard();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to reschedule workout");
    }
  }

  if (loading) {
    return <main className="flex min-h-screen items-center justify-center text-muted">Loading your adaptive OS...</main>;
  }

  return (
    <AppShell user={user} onLogout={logout}>
      <div className="space-y-5">
        <header className="panel rounded-xl p-6">
          <div className="flex flex-col justify-between gap-5 lg:flex-row lg:items-center">
            <div>
              <p className="mb-2 inline-flex items-center gap-2 rounded-full border border-white/10 bg-[#0b0f17] px-3 py-1 text-xs text-slate-200">
                <Radio className="h-3.5 w-3.5 text-limeGlow" />
                Realtime {realtime.status}
              </p>
              <h1 className="text-3xl font-semibold md:text-4xl">Good to see you, {user?.full_name?.split(" ")[0] || "Athlete"}.</h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">
                Your command center is live. It is tracking readiness, adherence, training, nutrition, and event signals.
              </p>
              {notice ? <p className="mt-3 text-sm text-limeGlow">{notice}</p> : null}
              {error ? <p className="mt-3 text-sm text-red-200">{error}</p> : null}
            </div>
            <div className="rounded-xl border border-white/10 bg-[#0b0f17] p-4">
              <div className="flex items-center gap-3">
                <Sparkles className="h-5 w-5 text-white" />
                <div>
                  <p className="text-sm font-semibold">Adaptive intelligence active</p>
                  <p className="text-xs text-muted">Events, recommendations, and memory are live.</p>
                </div>
              </div>
            </div>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="Readiness" value={dashboard?.readiness_score ?? "--"} helper="Recovery-adjusted score" tone="lime" icon={Brain} />
          <MetricCard label="Workout" value={dashboard?.today_workout?.status || "--"} helper={dashboard?.today_workout?.title || "Loading plan"} tone="cyan" icon={Activity} />
          <MetricCard label="Nutrition" value={dashboard?.nutrition?.calories ?? 0} helper={`${dashboard?.nutrition?.protein_g ?? 0}g protein logged`} tone="coral" icon={Salad} />
          <MetricCard label="Sleep" value={dashboard?.latest_sleep?.duration_hours ?? "--"} helper={dashboard?.latest_sleep ? "hours logged" : "Awaiting sleep log"} tone="white" icon={Moon} />
        </section>

        <section className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
          <GlassPanel className="p-6">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">Today's workout</h2>
                <p className="text-sm text-muted">{dashboard?.today_workout?.notes || "Your daily session appears here."}</p>
              </div>
              <Flame className="h-5 w-5 text-coralGlow" />
            </div>

            <div className="soft-panel rounded-xl p-4">
              <p className="text-2xl font-semibold">{dashboard?.today_workout?.title || "Loading..."}</p>
              <p className="mt-2 text-sm text-muted">
                {dashboard?.today_workout?.duration_minutes || 0} min - {dashboard?.today_workout?.planned_intensity || "moderate"} intensity
              </p>
              <p className="mt-2 text-sm capitalize text-slate-300">Status: {dashboard?.today_workout?.status || "scheduled"}</p>
              <div className="mt-5 flex flex-wrap gap-3">
                <Button onClick={() => updateWorkout("complete")} disabled={dashboard?.today_workout?.status !== "scheduled"}>
                  <CheckCircle2 className="h-4 w-4" />
                  Mark complete
                </Button>
                <Button variant="secondary" onClick={() => updateWorkout("miss")} disabled={dashboard?.today_workout?.status !== "scheduled"}>
                  <XCircle className="h-4 w-4" />
                  Mark missed
                </Button>
              </div>
              <div className="mt-4 flex flex-col gap-3 border-t subtle-divider pt-4 sm:flex-row">
                <input
                  type="date"
                  value={rescheduleDate}
                  onChange={(event) => setRescheduleDate(event.target.value)}
                  className="rounded-lg border border-white/10 bg-[#0b0f17] px-3 py-2 text-sm text-white outline-none"
                />
                <Button variant="ghost" onClick={rescheduleWorkout} disabled={dashboard?.today_workout?.status !== "scheduled" || !rescheduleDate}>
                  <CalendarClock className="h-4 w-4" />
                  Reschedule
                </Button>
              </div>
            </div>
          </GlassPanel>

          <GlassPanel className="p-6">
            <h2 className="text-lg font-semibold">Recommendations</h2>
            <div className="mt-4 space-y-3">
              {(dashboard?.recommendations || []).map((item) => (
                <div key={item.id} className="soft-panel rounded-xl p-4">
                  <div className="flex items-start justify-between gap-3">
                    <p className="text-sm font-semibold">{item.title}</p>
                    <span className="rounded-full bg-white/10 px-2 py-1 text-xs">{Math.round((item.confidence_score || 0.6) * 100)}%</span>
                  </div>
                  <p className="mt-1 text-sm text-muted">{item.body}</p>
                  {item.reasoning_summary ? <p className="mt-2 text-xs text-muted">{item.reasoning_summary}</p> : null}
                  <div className="mt-3 flex gap-2">
                    <Button
                      variant="secondary"
                      className="px-3 py-1.5 text-xs"
                      onClick={async () => {
                        await sendRecommendationFeedback(item.id, "accepted");
                        await loadDashboard();
                      }}
                    >
                      Accept
                    </Button>
                    <Button
                      variant="ghost"
                      className="px-3 py-1.5 text-xs"
                      onClick={async () => {
                        await sendRecommendationFeedback(item.id, "dismissed");
                        await loadDashboard();
                      }}
                    >
                      Dismiss
                    </Button>
                  </div>
                </div>
              ))}
              <div className="rounded-xl border border-white/10 bg-[#0b0f17] p-3 text-sm text-slate-300">
                <p className="font-medium text-white">Realtime activity</p>
                <p className="mt-1 text-muted">
                  {realtime.lastMessage?.type === "ai.event.processed"
                    ? `AI processed ${realtime.lastMessage.payload?.source_event?.replaceAll(".", " ") || "a recent event"} and refreshed recommendations.`
                    : realtime.status === "connected"
                      ? "Listening for plan, readiness, and recommendation updates."
                      : "Realtime connection is starting."}
                </p>
              </div>
            </div>
          </GlassPanel>
        </section>
      </div>
    </AppShell>
  );
}
