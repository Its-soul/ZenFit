"use client";

import { useEffect, useState } from "react";

import { DailyCheckInCard } from "@/components/product/DailyCheckInCard";
import { RecoveryStoryCard } from "@/components/product/RecoveryStoryCard";
import { ProtectedFeaturePage } from "@/components/layout/ProtectedFeaturePage";
import { todayIsoDate } from "@/lib/date";
import { createRecoveryCheckin, getReadiness } from "@/services/recoveryService";

function recoveryStory(readiness) {
  if (!readiness) {
    return {
      title: "ZenFit needs one body check-in.",
      cause: "No recovery signal has been saved yet today.",
      effect: "Without it, your plan cannot tell whether to push or protect energy.",
      recommendation: "Choose how you feel below. One tap is enough."
    };
  }
  if (readiness.readiness_score < 55) {
    return {
      title: "Recovery needs protection today.",
      cause: "Fatigue, soreness, or stress is elevated in your latest check-in.",
      effect: "Hard training may cost more motivation than it builds today.",
      recommendation: "Choose lighter movement and count it as momentum protected.",
      tone: "coral"
    };
  }
  if (readiness.readiness_score > 78) {
    return {
      title: "Your body is ready for more.",
      cause: "Your latest check-in shows lower strain and better readiness.",
      effect: "This is a good day for a focused main session.",
      recommendation: "Push with control, then recover well tonight.",
      tone: "gold"
    };
  }
  return {
    title: "Recovery is steady.",
    cause: "Your check-in does not show major strain today.",
    effect: "You can train normally if the warm-up feels good.",
    recommendation: "Start the planned session and adjust after the first set.",
    tone: "sage"
  };
}

export default function RecoveryPage() {
  const [readiness, setReadiness] = useState(null);
  const [selectedMood, setSelectedMood] = useState("okay");
  const [notice, setNotice] = useState("");

  async function loadReadiness() {
    setReadiness(await getReadiness());
  }

  useEffect(() => {
    loadReadiness();
  }, []);

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
    setNotice("Recovery check-in saved. ZenFit can now match the day to your body.");
    await loadReadiness();
  }

  const story = recoveryStory(readiness);

  return (
    <ProtectedFeaturePage
      title="Recovery"
      description="Understand what your body needs today, then train with less guesswork."
    >
      {notice ? <p className="mb-4 text-sm text-zenSage">{notice}</p> : null}
      <div className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
        <RecoveryStoryCard {...story} />
        <DailyCheckInCard selectedMood={selectedMood} onSelectMood={(mood) => setSelectedMood(mood.id)} onSave={saveMood} />
      </div>
    </ProtectedFeaturePage>
  );
}
