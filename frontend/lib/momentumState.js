export function buildMomentumContext({ dashboard, history }) {
  const points = history?.points || [];
  const workout = dashboard?.today_workout || {};
  const latestSleep = dashboard?.latest_sleep || {};
  const recent = points.slice(-14);

  return {
    workoutStatus: workout.status || "scheduled",
    readiness: dashboard?.readiness_score || null,
    sleepHours: latestSleep.duration_hours || null,
    proteinLogged: dashboard?.nutrition?.protein_g || 0,
    streak: calculateWorkoutStreak(points),
    missedRecently: recent.slice(-4).some((point) => point.workouts_missed > 0),
    weeklyWins: calculateWeeklyWins(points),
    lowSleepNights: recent.filter((point) => point.sleep_hours && point.sleep_hours < 6.5).length,
    recoveryTrend: getRecoveryTrend(recent)
  };
}

export function getMomentumState(context) {
  if (context.workoutStatus === "completed") {
    return {
      type: "celebration",
      tone: "gold",
      label: "Momentum protected",
      title: "You showed up today.",
      subtitle: "That is the habit. Everything else builds from here.",
      action: "Recover well tonight",
      coachPrompt: "Celebrate my progress"
    };
  }

  if (context.missedRecently) {
    return {
      type: "comeback",
      tone: "coral",
      label: "Comeback day",
      title: "Welcome back.",
      subtitle: "One smaller session is enough to rebuild rhythm.",
      action: "Start the comeback version",
      coachPrompt: "I missed yesterday"
    };
  }

  if (context.streak >= 3 && context.workoutStatus === "scheduled") {
    return {
      type: "streak-risk",
      tone: "gold",
      label: `${context.streak}-day rhythm`,
      title: "Protect your streak today.",
      subtitle: "A 10-minute version keeps momentum alive.",
      action: "Keep the streak alive",
      coachPrompt: "Keep me accountable"
    };
  }

  if ((context.readiness && context.readiness < 55) || (context.sleepHours && context.sleepHours < 6)) {
    return {
      type: "low-energy",
      tone: "sage",
      label: "Recovery matters today",
      title: "Energy looks low.",
      subtitle: "Protect momentum with lighter movement.",
      action: "Switch to lighter training",
      coachPrompt: "I'm tired today"
    };
  }

  if (context.readiness && context.readiness > 78 && (!context.sleepHours || context.sleepHours >= 7)) {
    return {
      type: "high-energy",
      tone: "lime",
      label: "Strong recovery",
      title: "Recovery is high today.",
      subtitle: "Push harder while your body is ready.",
      action: "Start the main session",
      coachPrompt: "Challenge me today"
    };
  }

  return {
    type: "steady",
    tone: "sage",
    label: "Momentum building",
    title: "Here is your best next step.",
    subtitle: "Keep today simple and protect the rhythm.",
    action: "Start today's plan",
    coachPrompt: "What should I do today?"
  };
}

export function getMomentumNarratives(context) {
  const streak = context.streak > 0 ? `${context.streak}-day workout streak` : "Start a streak today";
  const recovery =
    context.lowSleepNights >= 2
      ? "Recovery dipped after lower-sleep nights"
      : context.recoveryTrend === "rising"
        ? "Recovery is trending up"
        : "Recovery is steady enough to keep moving";
  const comeback = context.missedRecently ? "Momentum recovering after a missed session" : "No recent collapse in rhythm";

  return [
    { label: "Rhythm", value: streak, helper: streak.includes("Start") ? "One short session begins it." : "You are building proof." },
    { label: "Recovery story", value: recovery, helper: "Your plan should match your body." },
    { label: "Momentum", value: comeback, helper: context.missedRecently ? "Comeback days count." : "Keep the next action simple." }
  ];
}

export function getWorkoutIntent(momentum, workout) {
  if (momentum.type === "low-energy") return "Reduced intensity to protect consistency.";
  if (momentum.type === "comeback") return "Today focuses on rebuilding rhythm.";
  if (momentum.type === "high-energy") return "Recovery quality supports stronger compound work.";
  if (workout?.status === "completed") return "Session complete. Recovery is the next win.";
  return "Today focuses on steady strength and confidence.";
}

export function getEstimatedCalories(workout) {
  const minutes = workout?.duration_minutes || 35;
  const intensity = workout?.planned_intensity || "moderate";
  const multiplier = intensity === "high" ? 8 : intensity === "low" ? 4.5 : 6;
  return Math.round(minutes * multiplier);
}

export function getMuscleGroups(workout) {
  const title = (workout?.title || "").toLowerCase();
  if (title.includes("upper")) return ["Chest", "Back", "Shoulders", "Core"];
  if (title.includes("lower")) return ["Glutes", "Quads", "Hamstrings", "Core"];
  if (title.includes("cardio")) return ["Heart", "Legs", "Lungs"];
  return ["Legs", "Push", "Pull", "Core"];
}

export function getWorkoutExercises(workout, momentum) {
  if (momentum.type === "low-energy") return ["Mobility flow", "Easy squat pattern", "Light row", "Breathing cooldown"];
  if (momentum.type === "comeback") return ["Warm-up walk", "Goblet squat", "Incline push-up", "Carry"];
  const title = (workout?.title || "").toLowerCase();
  if (title.includes("strength")) return ["Goblet squat", "Push-up", "Row", "Romanian deadlift", "Carry"];
  return ["Warm-up", "Main movement", "Accessory work", "Core", "Cooldown"];
}

function calculateWorkoutStreak(points) {
  let streak = 0;
  for (let index = points.length - 1; index >= 0; index -= 1) {
    const point = points[index];
    if (point.workouts_completed > 0) streak += 1;
    else if (point.workouts_missed > 0) break;
  }
  return streak;
}

function calculateWeeklyWins(points) {
  return points.slice(-7).reduce((total, point) => {
    const workoutWin = point.workouts_completed > 0 ? 1 : 0;
    const sleepWin = point.sleep_hours >= 7 ? 1 : 0;
    const nutritionWin = point.protein_g >= 80 ? 1 : 0;
    return total + workoutWin + sleepWin + nutritionWin;
  }, 0);
}

function getRecoveryTrend(points) {
  const values = points.map((point) => point.readiness_score).filter(Boolean);
  if (values.length < 4) return "steady";
  const first = values.slice(0, Math.ceil(values.length / 2)).reduce((a, b) => a + b, 0) / Math.ceil(values.length / 2);
  const second = values.slice(Math.floor(values.length / 2)).reduce((a, b) => a + b, 0) / Math.ceil(values.length / 2);
  if (second - first > 5) return "rising";
  if (first - second > 5) return "falling";
  return "steady";
}
