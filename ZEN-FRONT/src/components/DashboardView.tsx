import React, { useState } from 'react';
import { 
  Footprints, 
  Flame, 
  Droplets, 
  Dumbbell, 
  HeartPulse, 
  UtensilsCrossed, 
  Plus, 
  CheckCircle, 
  ChevronRight, 
  Clock, 
  Award, 
  Sparkles,
  ArrowUpRight,
  RotateCcw
} from 'lucide-react';
import { DailyGoals, NutritionMacroSummary, WorkoutItem, ViewMode } from '../types';
import { weeklyActivityData } from '../data/mockData';

interface DashboardViewProps {
  goals: DailyGoals;
  macros: NutritionMacroSummary;
  todayWorkout: WorkoutItem;
  workoutCompleted: boolean;
  onToggleWorkoutCompleted: () => void;
  onUpdateGoals: (newGoals: Partial<DailyGoals>) => void;
  onSelectView: (view: ViewMode) => void;
  onOpenMealModal: () => void;
  onStartActiveWorkout: (workout: WorkoutItem) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  goals,
  macros,
  todayWorkout,
  workoutCompleted,
  onToggleWorkoutCompleted,
  onUpdateGoals,
  onSelectView,
  onOpenMealModal,
  onStartActiveWorkout,
}) => {
  const [hoveredDay, setHoveredDay] = useState<typeof weeklyActivityData[0] | null>(weeklyActivityData[3]);
  const [chartMode, setChartMode] = useState<'activity' | 'calories'>('activity');

  // Calculations for radial circles
  const stepsPct = Math.min(100, Math.round((goals.stepsCurrent / goals.stepsGoal) * 100));
  const caloriesPct = Math.min(100, Math.round((goals.caloriesCurrent / goals.caloriesGoal) * 100));
  const waterPct = Math.min(100, Math.round((goals.waterCurrentL / goals.waterGoalL) * 100));

  const proteinPct = Math.min(100, Math.round((macros.proteinCurrentG / macros.proteinGoalG) * 100));
  const carbsPct = Math.min(100, Math.round((macros.carbsCurrentG / macros.carbsGoalG) * 100));
  const fatPct = Math.min(100, Math.round((macros.fatCurrentG / macros.fatGoalG) * 100));

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* Top Banner Quick Greeting */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800/80 p-6 md:p-8 shadow-xl">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-80 h-80 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Optimal Neural Recovery State</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-black text-slate-100 tracking-tight">
              High-Performance Daily Overview
            </h2>
            <p className="text-xs md:text-sm text-slate-400 max-w-xl leading-relaxed">
              Your body is 85% recovered today. Focus on heavy compound lifts and maintain hydration targets.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => onStartActiveWorkout(todayWorkout)}
              className="flex items-center gap-2 px-5 py-3 rounded-xl bg-emerald-400 hover:bg-emerald-300 text-slate-950 font-bold text-xs md:text-sm shadow-lg shadow-emerald-500/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <Dumbbell className="w-4 h-4" />
              <span>Start Today's Session</span>
            </button>
            <button
              onClick={() => onSelectView('recovery')}
              className="p-3 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-bold transition-all"
              title="Recovery Analytics"
            >
              <HeartPulse className="w-4 h-4 text-emerald-400" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Goals Bento Card & Activity Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Bento 1: Daily Goals Radial Rings */}
        <div className="lg:col-span-5 bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <span>Daily Targets</span>
                <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">3 Active</span>
              </h3>
              <p className="text-xs text-slate-400">Real-time biological biometric progress</p>
            </div>
          </div>

          {/* Radial Rings SVG Canvas */}
          <div className="relative my-2 flex items-center justify-center py-4">
            <svg className="w-56 h-56 transform -rotate-90" viewBox="0 0 200 200">
              {/* Steps Ring (Outer - Emerald) */}
              <circle cx="100" cy="100" r="80" stroke="#1e293b" strokeWidth="12" fill="transparent" />
              <circle
                cx="100"
                cy="100"
                r="80"
                stroke="#10b981"
                strokeWidth="12"
                strokeDasharray={502.6}
                strokeDashoffset={502.6 - (502.6 * stepsPct) / 100}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-1000 ease-out"
              />

              {/* Calories Ring (Middle - Cyan) */}
              <circle cx="100" cy="100" r="62" stroke="#1e293b" strokeWidth="12" fill="transparent" />
              <circle
                cx="100"
                cy="100"
                r="62"
                stroke="#06b6d4"
                strokeWidth="12"
                strokeDasharray={389.5}
                strokeDashoffset={389.5 - (389.5 * caloriesPct) / 100}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-1000 ease-out"
              />

              {/* Water Ring (Inner - Blue) */}
              <circle cx="100" cy="100" r="44" stroke="#1e293b" strokeWidth="12" fill="transparent" />
              <circle
                cx="100"
                cy="100"
                r="44"
                stroke="#3b82f6"
                strokeWidth="12"
                strokeDasharray={276.4}
                strokeDashoffset={276.4 - (276.4 * waterPct) / 100}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-1000 ease-out"
              />
            </svg>

            {/* Center Summary Label */}
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center pointer-events-none">
              <span className="text-2xl font-black text-slate-100">{stepsPct}%</span>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Completed</span>
            </div>
          </div>

          {/* Biometrics Legend List with Quick Add Actions */}
          <div className="space-y-3 pt-2">
            {/* Steps Metric */}
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/50 border border-slate-800/60">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                  <Footprints className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-200">Steps</p>
                  <p className="text-xs text-slate-400">
                    <span className="text-emerald-400 font-semibold">{goals.stepsCurrent.toLocaleString()}</span> / {goals.stepsGoal.toLocaleString()}
                  </p>
                </div>
              </div>
              <button
                onClick={() => onUpdateGoals({ stepsCurrent: goals.stepsCurrent + 500 })}
                className="px-2.5 py-1 text-[11px] font-bold text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-lg transition-all flex items-center gap-1"
                title="Add 500 steps"
              >
                <Plus className="w-3 h-3 text-emerald-400" /> 500
              </button>
            </div>

            {/* Calories Metric */}
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/50 border border-slate-800/60">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
                  <Flame className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-200">Active Calories</p>
                  <p className="text-xs text-slate-400">
                    <span className="text-cyan-400 font-semibold">{goals.caloriesCurrent}</span> / {goals.caloriesGoal} kcal
                  </p>
                </div>
              </div>
              <button
                onClick={() => onUpdateGoals({ caloriesCurrent: goals.caloriesCurrent + 100 })}
                className="px-2.5 py-1 text-[11px] font-bold text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-lg transition-all flex items-center gap-1"
                title="Add 100 kcal"
              >
                <Plus className="w-3 h-3 text-cyan-400" /> 100
              </button>
            </div>

            {/* Water Hydration Metric */}
            <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/50 border border-slate-800/60">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                  <Droplets className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-200">Hydration</p>
                  <p className="text-xs text-slate-400">
                    <span className="text-blue-400 font-semibold">{goals.waterCurrentL.toFixed(1)}L</span> / {goals.waterGoalL.toFixed(1)}L
                  </p>
                </div>
              </div>
              <button
                onClick={() => onUpdateGoals({ waterCurrentL: Math.min(5, goals.waterCurrentL + 0.25) })}
                className="px-2.5 py-1 text-[11px] font-bold text-slate-300 bg-slate-800 hover:bg-slate-700 rounded-lg transition-all flex items-center gap-1"
                title="Add 250ml water"
              >
                <Plus className="w-3 h-3 text-blue-400" /> 250ml
              </button>
            </div>
          </div>
        </div>

        {/* Bento 2: Weekly Activity Performance Curve */}
        <div className="lg:col-span-7 bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-100">Weekly Activity Trends</h3>
              <p className="text-xs text-slate-400">Consistent power output & calorie expenditure</p>
            </div>

            <div className="flex items-center gap-2 bg-slate-950 p-1 rounded-xl border border-slate-800 self-start sm:self-auto">
              <button
                onClick={() => setChartMode('activity')}
                className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${
                  chartMode === 'activity' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Activity Score
              </button>
              <button
                onClick={() => setChartMode('calories')}
                className={`px-3 py-1 text-xs font-bold rounded-lg transition-all ${
                  chartMode === 'calories' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Calories
              </button>
            </div>
          </div>

          {/* Interactive Chart Canvas */}
          <div className="relative my-4 h-64 w-full flex items-end justify-between px-2 pt-8">
            {/* Background Grid Lines */}
            <div className="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-20">
              <div className="border-b border-slate-700 w-full" />
              <div className="border-b border-slate-700 w-full" />
              <div className="border-b border-slate-700 w-full" />
              <div className="border-b border-slate-700 w-full" />
            </div>

            {/* SVG Path Curve */}
            <svg className="absolute inset-0 w-full h-full overflow-visible pointer-events-none" preserveAspectRatio="none" viewBox="0 0 700 200">
              <defs>
                <linearGradient id="curveGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              <path
                d="M 50 120 Q 150 70 250 40 T 450 60 T 650 140"
                fill="none"
                stroke="#10b981"
                strokeWidth="3.5"
                strokeLinecap="round"
              />
              <path
                d="M 50 120 Q 150 70 250 40 T 450 60 T 650 140 L 650 200 L 50 200 Z"
                fill="url(#curveGradient)"
              />
            </svg>

            {/* Interactive Day Nodes */}
            {weeklyActivityData.map((d, idx) => {
              const value = chartMode === 'activity' ? d.activityScore : d.calories;
              const maxVal = chartMode === 'activity' ? 100 : 1000;
              const barHeightPct = Math.min(100, Math.max(20, (value / maxVal) * 100));
              const isHovered = hoveredDay?.day === d.day;

              return (
                <div
                  key={d.day}
                  onMouseEnter={() => setHoveredDay(d)}
                  className="flex flex-col items-center gap-2 z-10 flex-1 group cursor-pointer"
                >
                  {/* Tooltip on Hover */}
                  {isHovered && (
                    <div className="absolute top-0 transform -translate-y-full bg-slate-950 border border-emerald-500/30 text-slate-100 text-[11px] p-2.5 rounded-xl shadow-2xl z-30 pointer-events-none animate-fade-in flex flex-col gap-0.5 whitespace-nowrap">
                      <span className="font-bold text-emerald-400">{d.day} Performance</span>
                      <span>Score: <strong className="text-white">{d.activityScore} pts</strong></span>
                      <span>Burned: <strong className="text-cyan-400">{d.calories} kcal</strong></span>
                      <span>Steps: <strong className="text-slate-300">{d.steps.toLocaleString()}</strong></span>
                    </div>
                  )}

                  {/* Vertical Column Bar */}
                  <div className="w-8 md:w-10 bg-slate-950/60 rounded-xl p-1 border border-slate-800/80 flex flex-col justify-end h-44 group-hover:border-emerald-500/50 transition-all">
                    <div
                      style={{ height: `${barHeightPct}%` }}
                      className={`w-full rounded-lg transition-all duration-500 ${
                        isHovered 
                          ? 'bg-gradient-to-t from-emerald-500 to-teal-300 shadow-lg shadow-emerald-500/30' 
                          : 'bg-gradient-to-t from-slate-800 to-slate-700 group-hover:from-emerald-600/60 group-hover:to-teal-500/60'
                      }`}
                    />
                  </div>

                  <span className={`text-xs font-bold transition-colors ${isHovered ? 'text-emerald-400' : 'text-slate-400'}`}>
                    {d.day}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Interactive Footer Summary of Hovered Day */}
          <div className="mt-2 p-3 rounded-2xl bg-slate-950/60 border border-slate-800/60 flex items-center justify-between text-xs">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                <Award className="w-4 h-4" />
              </div>
              <div>
                <span className="text-slate-400">Peak Output Day: </span>
                <span className="font-bold text-slate-100">Saturday (96 Activity Score)</span>
              </div>
            </div>
            <button 
              onClick={() => onSelectView('progress')}
              className="text-emerald-400 font-bold hover:underline flex items-center gap-1"
            >
              <span>Full Analytics</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

      </div>

      {/* Bottom Row: 3 Key Bento Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        {/* Card 1: Today's Scheduled Workout */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl flex flex-col justify-between relative overflow-hidden group">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                Today's Workout
              </span>
              <span className="text-xs text-slate-400 font-medium flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                {todayWorkout.durationMinutes} min
              </span>
            </div>

            <div>
              <h4 className="text-lg font-bold text-slate-100 group-hover:text-emerald-300 transition-colors">
                {todayWorkout.title}
              </h4>
              <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                {todayWorkout.description}
              </p>
            </div>

            {/* Trainer Avatar & Level Tag */}
            <div className="flex items-center justify-between pt-2 border-t border-slate-800/60">
              <div className="flex items-center gap-2.5">
                <img
                  src={todayWorkout.trainerAvatar}
                  alt={todayWorkout.trainerName}
                  className="w-7 h-7 rounded-full object-cover ring-2 ring-emerald-500/30"
                />
                <span className="text-xs font-semibold text-slate-300">{todayWorkout.trainerName}</span>
              </div>
              <span className="text-[11px] font-bold text-slate-400 bg-slate-800 px-2.5 py-0.5 rounded-full">
                {todayWorkout.level}
              </span>
            </div>
          </div>

          <div className="mt-6 space-y-2">
            <button
              onClick={() => onStartActiveWorkout(todayWorkout)}
              className="w-full py-2.5 px-4 rounded-xl font-bold text-xs bg-emerald-400 hover:bg-emerald-300 text-slate-950 transition-all flex items-center justify-center gap-2 shadow-md shadow-emerald-500/10"
            >
              <Dumbbell className="w-3.5 h-3.5" />
              <span>Launch Interactive Player</span>
            </button>

            <button
              onClick={onToggleWorkoutCompleted}
              className={`w-full py-2 px-4 rounded-xl font-semibold text-xs border transition-all flex items-center justify-center gap-2 ${
                workoutCompleted
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                  : 'bg-slate-800/60 hover:bg-slate-800 text-slate-300 border-slate-700'
              }`}
            >
              <CheckCircle className={`w-3.5 h-3.5 ${workoutCompleted ? 'text-emerald-400' : 'text-slate-400'}`} />
              <span>{workoutCompleted ? 'Completed Today! 🔥' : 'Mark Completed'}</span>
            </button>
          </div>
        </div>

        {/* Card 2: Recovery Status Radial Gauge */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-teal-400 bg-teal-500/10 px-2.5 py-1 rounded-lg border border-teal-500/20">
                Recovery Status
              </span>
              <span className="text-xs font-bold text-emerald-400">High Prime</span>
            </div>

            <div className="flex items-center gap-4 py-2">
              <div className="relative w-20 h-20 flex-shrink-0">
                <svg className="w-20 h-20 transform -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="40" stroke="#1e293b" strokeWidth="8" fill="transparent" />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke="#10b981"
                    strokeWidth="8"
                    strokeDasharray={251.2}
                    strokeDashoffset={251.2 - (251.2 * 85) / 100}
                    strokeLinecap="round"
                    fill="transparent"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center font-black text-lg text-slate-100">
                  85%
                </div>
              </div>

              <div className="space-y-1">
                <p className="text-xs font-bold text-slate-200">Optimal Readiness</p>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  HRV is 68ms (+12% above average). Central nervous system is ready for heavy load.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/60 text-xs">
              <div className="bg-slate-950/60 p-2 rounded-xl border border-slate-800/60">
                <span className="text-[10px] text-slate-400 block">Sleep Quality</span>
                <span className="font-bold text-slate-200">8.2 hrs (High)</span>
              </div>
              <div className="bg-slate-950/60 p-2 rounded-xl border border-slate-800/60">
                <span className="text-[10px] text-slate-400 block">Resting HR</span>
                <span className="font-bold text-emerald-400">52 bpm</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => onSelectView('recovery')}
            className="mt-6 w-full py-2.5 px-4 rounded-xl font-bold text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all flex items-center justify-center gap-1.5"
          >
            <span>View Recovery Insights</span>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          </button>
        </div>

        {/* Card 3: Nutrition Macros Overview */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-lg border border-cyan-500/20">
                Daily Nutrition
              </span>
              <span className="text-xs font-semibold text-slate-400">1,800 kcal</span>
            </div>

            <div className="space-y-3 py-1">
              {/* Protein Bar */}
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium text-slate-300">Protein</span>
                  <span className="text-slate-400 font-mono"><strong className="text-emerald-400">{macros.proteinCurrentG}g</strong> / {macros.proteinGoalG}g</span>
                </div>
                <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                  <div style={{ width: `${proteinPct}%` }} className="h-full bg-emerald-400 rounded-full" />
                </div>
              </div>

              {/* Carbs Bar */}
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium text-slate-300">Carbohydrates</span>
                  <span className="text-slate-400 font-mono"><strong className="text-cyan-400">{macros.carbsCurrentG}g</strong> / {macros.carbsGoalG}g</span>
                </div>
                <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                  <div style={{ width: `${carbsPct}%` }} className="h-full bg-cyan-400 rounded-full" />
                </div>
              </div>

              {/* Fats Bar */}
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium text-slate-300">Healthy Fats</span>
                  <span className="text-slate-400 font-mono"><strong className="text-amber-400">{macros.fatCurrentG}g</strong> / {macros.fatGoalG}g</span>
                </div>
                <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                  <div style={{ width: `${fatPct}%` }} className="h-full bg-amber-400 rounded-full" />
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 flex items-center gap-2">
            <button
              onClick={onOpenMealModal}
              className="flex-1 py-2.5 px-3 rounded-xl font-bold text-xs bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/30 transition-all flex items-center justify-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5 text-cyan-400" />
              <span>Log Meal / AI Scan</span>
            </button>
            <button
              onClick={() => onSelectView('nutrition')}
              className="py-2.5 px-3 rounded-xl font-bold text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all"
            >
              Plan
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
