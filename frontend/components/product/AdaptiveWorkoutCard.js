"use client";

import { motion } from "framer-motion";
import { CalendarDays, CheckCircle2, Dumbbell, Flame, MoveRight, X } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { getEstimatedCalories, getMuscleGroups, getWorkoutExercises, getWorkoutIntent } from "@/lib/momentumState";

export function AdaptiveWorkoutCard({ workout, momentum, onComplete, onSkip, onMove }) {
  const exercises = getWorkoutExercises(workout, momentum);
  const muscleGroups = getMuscleGroups(workout);
  const calories = getEstimatedCalories(workout);
  const canAct = workout?.status === "scheduled";

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      className="panel rounded-[1.5rem] p-6"
    >
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">
        <div>
          <p className="flex items-center gap-2 text-sm font-semibold text-zenSage">
            <Dumbbell className="h-4 w-4" />
            Today's workout
          </p>
          <h2 className="mt-2 text-3xl font-semibold tracking-[-0.02em]">{workout?.title || "Full Body Foundation"}</h2>
          <p className="mt-2 text-sm text-muted">
            {workout?.duration_minutes || 35} min / {workout?.planned_intensity || "moderate"} difficulty / about {calories} kcal
          </p>
        </div>
        <span className="rounded-full bg-white/10 px-3 py-1 text-xs capitalize text-slate-200">{workout?.status || "scheduled"}</span>
      </div>

      <div className="mt-5 rounded-2xl bg-zenCream p-4 text-[#121711]">
        <p className="text-sm font-semibold">Workout intent</p>
        <p className="mt-1 text-sm leading-6 text-slate-700">{getWorkoutIntent(momentum, workout)}</p>
      </div>

      <div className="mt-5 flex flex-wrap gap-2">
        {muscleGroups.map((group) => (
          <span key={group} className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-200">
            {group}
          </span>
        ))}
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        {exercises.map((exercise, index) => (
          <div key={exercise} className="soft-panel rounded-2xl p-4">
            <p className="text-xs text-muted">Move {index + 1}</p>
            <p className="mt-1 font-semibold">{exercise}</p>
          </div>
        ))}
      </div>

      <div className="mt-6 flex flex-col gap-3 border-t subtle-divider pt-5 sm:flex-row">
        <Button onClick={onComplete} disabled={!canAct} className="shadow-[0_18px_60px_rgba(245,241,232,0.12)]">
          <CheckCircle2 className="h-4 w-4" />
          Complete workout
        </Button>
        <Button variant="secondary" onClick={onSkip} disabled={!canAct}>
          <X className="h-4 w-4" />
          Need lighter today
        </Button>
        <Button variant="ghost" onClick={onMove} disabled={!canAct}>
          <CalendarDays className="h-4 w-4" />
          Move session
        </Button>
      </div>

      <div className="mt-5 flex items-center gap-2 text-sm text-muted">
        <Flame className="h-4 w-4 text-zenGold" />
        <span>{momentum.type === "comeback" ? "Comeback sessions count double emotionally." : "Protect the rhythm before chasing perfection."}</span>
        <MoveRight className="h-4 w-4" />
      </div>
    </motion.section>
  );
}
