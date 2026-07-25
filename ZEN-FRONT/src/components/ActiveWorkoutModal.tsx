import React, { useState, useEffect } from 'react';
import { 
  X, 
  Play, 
  Pause, 
  SkipForward, 
  RotateCcw, 
  CheckCircle2, 
  Flame, 
  Clock, 
  Dumbbell, 
  Trophy,
  Volume2
} from 'lucide-react';
import { WorkoutItem } from '../types';

interface ActiveWorkoutModalProps {
  workout: WorkoutItem;
  onClose: () => void;
  onComplete: () => void;
}

export const ActiveWorkoutModal: React.FC<ActiveWorkoutModalProps> = ({
  workout,
  onClose,
  onComplete,
}) => {
  const [currentExerciseIndex, setCurrentExerciseIndex] = useState(0);
  const [currentSet, setCurrentSet] = useState(1);
  const [timerSeconds, setTimerSeconds] = useState(45);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [isWorkoutFinished, setIsWorkoutFinished] = useState(false);

  const currentExercise = workout.exercises[currentExerciseIndex] || workout.exercises[0];

  useEffect(() => {
    let interval: any = null;
    if (isTimerRunning && timerSeconds > 0) {
      interval = setInterval(() => {
        setTimerSeconds((prev) => prev - 1);
      }, 1000);
    } else if (timerSeconds === 0) {
      setIsTimerRunning(false);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning, timerSeconds]);

  const handleNextSet = () => {
    if (currentSet < currentExercise.sets) {
      setCurrentSet((prev) => prev + 1);
      setTimerSeconds(45); // Reset rest timer
      setIsTimerRunning(true);
    } else {
      // Move to next exercise
      if (currentExerciseIndex < workout.exercises.length - 1) {
        setCurrentExerciseIndex((prev) => prev + 1);
        setCurrentSet(1);
        setTimerSeconds(60);
        setIsTimerRunning(true);
      } else {
        // Complete Workout
        setIsWorkoutFinished(true);
        onComplete();
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/90 backdrop-blur-xl flex items-center justify-center p-4 animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-xl w-full p-6 md:p-8 space-y-6 shadow-2xl relative overflow-hidden">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-slate-200 p-2"
        >
          <X className="w-5 h-5" />
        </button>

        {isWorkoutFinished ? (
          <div className="py-12 text-center space-y-4 animate-scale-up">
            <div className="w-20 h-20 rounded-full bg-emerald-500/20 border-2 border-emerald-400 text-emerald-400 flex items-center justify-center mx-auto shadow-2xl shadow-emerald-500/30">
              <Trophy className="w-10 h-10" />
            </div>
            <h2 className="text-3xl font-black text-slate-100">Workout Crushed! 🔥</h2>
            <p className="text-sm text-slate-300 max-w-md mx-auto">
              You completed <strong className="text-emerald-400">{workout.title}</strong>! Estimated <strong className="text-cyan-400">{workout.caloriesBurnEstimate} kcal</strong> burned. Your streak is updated!
            </p>
            <button
              onClick={onClose}
              className="px-8 py-3 rounded-2xl bg-emerald-400 hover:bg-emerald-300 text-slate-950 font-black text-sm shadow-xl shadow-emerald-500/20"
            >
              Back to Dashboard
            </button>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="space-y-1">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-bold text-emerald-400 uppercase tracking-wider">
                  Exercise {currentExerciseIndex + 1} of {workout.exercises.length}
                </span>
                <span className="font-mono bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
                  {workout.title}
                </span>
              </div>
              <h3 className="text-2xl font-black text-slate-100">{currentExercise.name}</h3>
            </div>

            {/* Set Progress Indicators */}
            <div className="flex items-center gap-2">
              {Array.from({ length: currentExercise.sets }).map((_, idx) => (
                <div
                  key={idx}
                  className={`flex-1 h-3 rounded-full transition-all ${
                    idx + 1 < currentSet
                      ? 'bg-emerald-400'
                      : idx + 1 === currentSet
                      ? 'bg-emerald-500/40 border border-emerald-400 animate-pulse'
                      : 'bg-slate-800'
                  }`}
                />
              ))}
            </div>

            {/* Main Interactive Exercise Card */}
            <div className="bg-slate-950/80 border border-slate-800/80 rounded-2xl p-6 text-center space-y-4 shadow-inner">
              <div className="flex items-center justify-center gap-6">
                <div>
                  <span className="text-xs text-slate-500 font-bold uppercase block">Current Set</span>
                  <span className="text-3xl font-black text-slate-100">
                    {currentSet} <span className="text-xs text-slate-500 font-normal">/ {currentExercise.sets}</span>
                  </span>
                </div>
                <div className="w-px h-10 bg-slate-800" />
                <div>
                  <span className="text-xs text-slate-500 font-bold uppercase block">Target Reps</span>
                  <span className="text-3xl font-black text-emerald-400">{currentExercise.reps}</span>
                </div>
              </div>

              {/* Timer & Controls */}
              <div className="pt-2">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider block mb-1">Rest Interval Timer</span>
                <div className="text-4xl font-black text-cyan-400 font-mono tracking-tight">
                  00:{timerSeconds < 10 ? `0${timerSeconds}` : timerSeconds}
                </div>

                <div className="flex items-center justify-center gap-3 mt-3">
                  <button
                    onClick={() => setIsTimerRunning(!isTimerRunning)}
                    className="p-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 transition-all"
                    title={isTimerRunning ? 'Pause' : 'Start'}
                  >
                    {isTimerRunning ? <Pause className="w-5 h-5 text-amber-400" /> : <Play className="w-5 h-5 text-emerald-400 fill-emerald-400" />}
                  </button>
                  <button
                    onClick={() => setTimerSeconds(45)}
                    className="p-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 transition-all"
                    title="Reset Timer"
                  >
                    <RotateCcw className="w-5 h-5 text-slate-400" />
                  </button>
                </div>
              </div>
            </div>

            {/* Next Set Button */}
            <button
              onClick={handleNextSet}
              className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-emerald-400 via-teal-400 to-emerald-500 hover:from-emerald-300 hover:to-teal-400 text-slate-950 font-black text-sm transition-all flex items-center justify-center gap-2 shadow-xl shadow-emerald-500/20"
            >
              <span>{currentSet < currentExercise.sets ? 'Complete Set & Rest' : currentExerciseIndex < workout.exercises.length - 1 ? 'Next Exercise' : 'Finish Workout! 🔥'}</span>
              <SkipForward className="w-4 h-4 fill-slate-950" />
            </button>
          </>
        )}
      </div>
    </div>
  );
};
