"use client";

import { useEffect, useMemo, useState } from "react";

import { ActionSheet } from "@/components/product/ActionSheet";
import { AdaptiveWorkoutCard } from "@/components/product/AdaptiveWorkoutCard";
import { CelebrationToast } from "@/components/product/CelebrationToast";
import { CoachInterventionCard } from "@/components/product/CoachInterventionCard";
import { DailyCheckInCard } from "@/components/product/DailyCheckInCard";
import { HelpfulNudges } from "@/components/product/HelpfulNudges";
import { MomentumHero } from "@/components/product/MomentumHero";
import { MomentumStrip } from "@/components/product/MomentumStrip";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/hooks/useAuth";
import { useRealtimeDashboard } from "@/hooks/useRealtimeDashboard";
import { todayIsoDate } from "@/lib/date";
import { buildMomentumContext, getMomentumNarratives, getMomentumState } from "@/lib/momentumState";
import { streamCoachMessage } from "@/services/aiCoachService";
import { getAnalyticsHistory } from "@/services/analyticsService";
import { getTodayDashboard } from "@/services/dashboardService";
import { createRecoveryCheckin } from "@/services/recoveryService";
import { sendRecommendationFeedback } from "@/services/recommendationService";
import { completeWorkoutSession, missWorkoutSession, rescheduleWorkoutSession } from "@/services/workoutService";

export default function DashboardPage() {
  const { user, loading, logout } = useAuth({ requireAuth: true });
  const realtime = useRealtimeDashboard();
  const [dashboard, setDashboard] = useState(null);
  const [history, setHistory] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [celebration, setCelebration] = useState("");
  const [rescheduleOpen, setRescheduleOpen] = useState(false);
  const [rescheduleDate, setRescheduleDate] = useState("");
  const [selectedMood, setSelectedMood] = useState("okay");
  const [coachInput, setCoachInput] = useState("");
  const [coachReply, setCoachReply] = useState("Tell me what feels hardest today. I will help you protect momentum.");
  const [coachLoading, setCoachLoading] = useState(false);

  async function loadToday() {
    try {
      const [today, progress] = await Promise.all([getTodayDashboard(), getAnalyticsHistory(30)]);
      setDashboard(today);
      setHistory(progress);
      setError("");
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "We could not load your plan yet.");
    }
  }

  useEffect(() => {
    if (!loading && user) queueMicrotask(loadToday);
  }, [loading, user]);

  useEffect(() => {
    if (realtime.lastMessage?.type === "ai.event.processed") {
      queueMicrotask(() => {
        setNotice("Your plan adjusted around your latest activity.");
        loadToday();
      });
    }
  }, [realtime.lastMessage]);

  useEffect(() => {
    if (!celebration) return;
    const timeout = setTimeout(() => setCelebration(""), 3600);
    return () => clearTimeout(timeout);
  }, [celebration]);

  const context = useMemo(() => buildMomentumContext({ dashboard, history }), [dashboard, history]);
  const momentum = useMemo(() => getMomentumState(context), [context]);
  const narratives = useMemo(() => getMomentumNarratives(context), [context]);
  const workout = dashboard?.today_workout;

  async function refreshWithCelebration(message) {
    setCelebration(message);
    setNotice(message);
    await loadToday();
  }

  async function completeWorkout() {
    if (!workout?.id || workout.status !== "scheduled") return;
    try {
      await completeWorkoutSession(workout.id);
      await refreshWithCelebration("You showed up today. Momentum protected.");
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "We could not update your workout.");
    }
  }

  async function skipWorkout() {
    if (!workout?.id || workout.status !== "scheduled") return;
    try {
      await missWorkoutSession(workout.id);
      await refreshWithCelebration("No guilt. ZenFit will help you restart small.");
      askCoach("I need a shorter workout today");
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "We could not adjust your workout.");
    }
  }

  async function moveWorkout() {
    if (!workout?.id || !rescheduleDate || workout.status !== "scheduled") return;
    try {
      await rescheduleWorkoutSession(workout.id, {
        scheduled_date: rescheduleDate,
        reason: "Moved from Today"
      });
      setRescheduleOpen(false);
      setRescheduleDate("");
      await refreshWithCelebration("Workout moved. Rhythm protected.");
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "We could not move this workout.");
    }
  }

  async function saveMood(mood) {
    setSelectedMood(mood.id);
    const fatigue = Math.max(1, Math.min(10, 11 - mood.energy));
    const stress = Math.max(1, Math.min(10, mood.stress));
    const soreness = Math.max(1, Math.min(10, Math.round((11 - mood.motivation + stress) / 2)));
    await createRecoveryCheckin({
      checkin_date: todayIsoDate(),
      fatigue_score: fatigue,
      soreness_score: soreness,
      stress_score: stress,
      notes: `${mood.label}: ${mood.response}`
    });
    await refreshWithCelebration(`${mood.label} logged. Today's plan can meet you where you are.`);
  }

  async function askCoach(prompt) {
    const message = (prompt || coachInput).trim();
    if (!message) return;
    setCoachInput("");
    setCoachLoading(true);
    setCoachReply("");
    let streamed = "";
    try {
      await streamCoachMessage(message, {
        onToken: (token) => {
          streamed += token;
          setCoachReply(streamed);
        },
        onMetadata: (metadata) => setCoachReply(metadata.message || streamed)
      });
    } catch {
      setCoachReply("I am having trouble replying, but the next best move is simple: make the session shorter, then count it.");
    } finally {
      setCoachLoading(false);
    }
  }

  async function handleNudgeFeedback(id, feedback) {
    await sendRecommendationFeedback(id, feedback);
    await loadToday();
    if (feedback === "accepted") setCelebration("Good choice. You turned guidance into momentum.");
  }

  if (loading) {
    return <main className="flex min-h-screen items-center justify-center text-muted">Preparing your momentum...</main>;
  }

  return (
    <AppShell user={user} onLogout={logout}>
      <div className="space-y-5 pb-24 md:pb-0">
        <MomentumHero momentum={momentum} userName={user?.full_name?.split(" ")[0]} notice={notice} error={error} />

        <section className="grid gap-5 xl:grid-cols-[1.08fr_0.92fr]">
          <AdaptiveWorkoutCard
            workout={workout}
            momentum={momentum}
            onComplete={completeWorkout}
            onSkip={skipWorkout}
            onMove={() => setRescheduleOpen(true)}
          />
          <div className="grid gap-5">
            <DailyCheckInCard selectedMood={selectedMood} onSelectMood={(mood) => setSelectedMood(mood.id)} onSave={saveMood} />
            <CoachInterventionCard
              momentum={momentum}
              reply={coachReply}
              input={coachInput}
              loading={coachLoading}
              onInputChange={setCoachInput}
              onAsk={askCoach}
            />
          </div>
        </section>

        <MomentumStrip narratives={narratives} />
        <HelpfulNudges items={dashboard?.recommendations || []} onFeedback={handleNudgeFeedback} />
      </div>

      <div className="fixed inset-x-4 bottom-4 z-30 md:hidden">
        <Button className="w-full rounded-2xl py-3 shadow-[0_12px_32px_rgba(0,0,0,0.3)]" onClick={completeWorkout} disabled={workout?.status !== "scheduled"}>
          {momentum.action}
        </Button>
      </div>

      <ActionSheet open={rescheduleOpen} title="Move this session" onClose={() => setRescheduleOpen(false)}>
        <p className="text-sm leading-6 text-muted">Moving a workout is better than disappearing. Choose the next realistic day.</p>
        <div className="mt-4 flex flex-col gap-3 sm:flex-row">
          <Input type="date" value={rescheduleDate} onChange={(event) => setRescheduleDate(event.target.value)} />
          <Button onClick={moveWorkout} disabled={!rescheduleDate}>Move workout</Button>
        </div>
      </ActionSheet>

      <CelebrationToast message={celebration} />
    </AppShell>
  );
}
