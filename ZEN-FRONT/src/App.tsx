import React, { useState, useEffect } from 'react';
import { ViewMode, UserProfile, DailyGoals, NutritionMacroSummary, WorkoutItem, MealItem, SleepLog, PersonalRecord } from './types';
import { 
  initialUserProfile, 
  initialDailyGoals, 
  initialMacroSummary, 
  initialWorkouts, 
  initialMeals, 
  initialSleepLogs, 
  initialTrainers, 
  initialPersonalRecords 
} from './data/mockData';

import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardView } from './components/DashboardView';
import { WorkoutsView } from './components/WorkoutsView';
import { NutritionView } from './components/NutritionView';
import { RecoveryView } from './components/RecoveryView';
import { ProgressView } from './components/ProgressView';
import { TrainersView } from './components/TrainersView';
import { LandingView } from './components/LandingView';
import { ActiveWorkoutModal } from './components/ActiveWorkoutModal';
import { AICoachDrawer } from './components/AICoachDrawer';
import { Footer } from './components/Footer';

export default function App() {
  const [currentView, setCurrentView] = useState<ViewMode>('dashboard');
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [showAICoach, setShowAICoach] = useState(false);

  // Core App State with LocalStorage Sync
  const [user, setUser] = useState<UserProfile>(() => {
    const saved = localStorage.getItem('zenfit_user');
    return saved ? JSON.parse(saved) : initialUserProfile;
  });

  const [goals, setGoals] = useState<DailyGoals>(() => {
    const saved = localStorage.getItem('zenfit_goals');
    return saved ? JSON.parse(saved) : initialDailyGoals;
  });

  const [macros, setMacros] = useState<NutritionMacroSummary>(() => {
    const saved = localStorage.getItem('zenfit_macros');
    return saved ? JSON.parse(saved) : initialMacroSummary;
  });

  const [workouts, setWorkouts] = useState<WorkoutItem[]>(() => {
    const saved = localStorage.getItem('zenfit_workouts');
    return saved ? JSON.parse(saved) : initialWorkouts;
  });

  const [meals, setMeals] = useState<MealItem[]>(() => {
    const saved = localStorage.getItem('zenfit_meals');
    return saved ? JSON.parse(saved) : initialMeals;
  });

  const [sleepLogs, setSleepLogs] = useState<SleepLog[]>(() => {
    const saved = localStorage.getItem('zenfit_sleep');
    return saved ? JSON.parse(saved) : initialSleepLogs;
  });

  const [personalRecords, setPersonalRecords] = useState<PersonalRecord[]>(() => {
    const saved = localStorage.getItem('zenfit_prs');
    return saved ? JSON.parse(saved) : initialPersonalRecords;
  });

  const [todayWorkoutCompleted, setTodayWorkoutCompleted] = useState(false);
  const [activeWorkoutPlayer, setActiveWorkoutPlayer] = useState<WorkoutItem | null>(null);

  // Sync to local storage
  useEffect(() => { localStorage.setItem('zenfit_user', JSON.stringify(user)); }, [user]);
  useEffect(() => { localStorage.setItem('zenfit_goals', JSON.stringify(goals)); }, [goals]);
  useEffect(() => { localStorage.setItem('zenfit_macros', JSON.stringify(macros)); }, [macros]);
  useEffect(() => { localStorage.setItem('zenfit_workouts', JSON.stringify(workouts)); }, [workouts]);
  useEffect(() => { localStorage.setItem('zenfit_meals', JSON.stringify(meals)); }, [meals]);
  useEffect(() => { localStorage.setItem('zenfit_sleep', JSON.stringify(sleepLogs)); }, [sleepLogs]);
  useEffect(() => { localStorage.setItem('zenfit_prs', JSON.stringify(personalRecords)); }, [personalRecords]);

  // Handler for goal updates
  const handleUpdateGoals = (newGoals: Partial<DailyGoals>) => {
    setGoals((prev) => ({ ...prev, ...newGoals }));
  };

  // Handler for adding new meal
  const handleAddMeal = (newMeal: MealItem) => {
    setMeals((prev) => [newMeal, ...prev]);
    setMacros((prev) => ({
      ...prev,
      proteinCurrentG: prev.proteinCurrentG + newMeal.proteinG,
      carbsCurrentG: prev.carbsCurrentG + newMeal.carbsG,
      fatCurrentG: prev.fatCurrentG + newMeal.fatG,
    }));
    setGoals((prev) => ({
      ...prev,
      caloriesCurrent: prev.caloriesCurrent + newMeal.calories,
    }));
  };

  // Handler for deleting meal
  const handleDeleteMeal = (mealId: string) => {
    const target = meals.find((m) => m.id === mealId);
    if (target) {
      setMeals((prev) => prev.filter((m) => m.id !== mealId));
      setMacros((prev) => ({
        ...prev,
        proteinCurrentG: Math.max(0, prev.proteinCurrentG - target.proteinG),
        carbsCurrentG: Math.max(0, prev.carbsCurrentG - target.carbsG),
        fatCurrentG: Math.max(0, prev.fatCurrentG - target.fatG),
      }));
      setGoals((prev) => ({
        ...prev,
        caloriesCurrent: Math.max(0, prev.caloriesCurrent - target.calories),
      }));
    }
  };

  // Handler for adding custom workout
  const handleAddCustomWorkout = (workout: WorkoutItem) => {
    setWorkouts((prev) => [workout, ...prev]);
  };

  // Handler for adding sleep log
  const handleAddSleepLog = (log: SleepLog) => {
    setSleepLogs((prev) => [log, ...prev]);
  };

  // Handler for adding PR
  const handleAddPR = (pr: PersonalRecord) => {
    setPersonalRecords((prev) => [pr, ...prev]);
  };

  // Toggle workout completion
  const handleToggleWorkoutCompleted = () => {
    setTodayWorkoutCompleted(!todayWorkoutCompleted);
    if (!todayWorkoutCompleted) {
      setUser((prev) => ({ ...prev, streakDays: prev.streakDays + 1 }));
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased selection:bg-emerald-500/30 selection:text-emerald-200 flex flex-col">
      {/* Sidebar Navigation */}
      <Sidebar
        currentView={currentView}
        onSelectView={setCurrentView}
        onStartWorkout={() => setActiveWorkoutPlayer(workouts[0])}
        isOpenMobile={isMobileSidebarOpen}
        onCloseMobile={() => setIsMobileSidebarOpen(false)}
        streakDays={user.streakDays}
      />

      {/* Main Content Area */}
      <div className="lg:pl-64 flex-1 flex flex-col min-w-0">
        {/* Sticky Header */}
        <Header
          user={user}
          currentView={currentView}
          onOpenMobileSidebar={() => setIsMobileSidebarOpen(true)}
          onToggleAICoach={() => setShowAICoach(!showAICoach)}
          onSelectView={setCurrentView}
        />

        {/* View Router Canvas */}
        <main className="flex-1 px-4 lg:px-8 pt-6 max-w-7xl w-full mx-auto">
          {currentView === 'dashboard' && (
            <DashboardView
              goals={goals}
              macros={macros}
              todayWorkout={workouts[0]}
              workoutCompleted={todayWorkoutCompleted}
              onToggleWorkoutCompleted={handleToggleWorkoutCompleted}
              onUpdateGoals={handleUpdateGoals}
              onSelectView={setCurrentView}
              onOpenMealModal={() => setCurrentView('nutrition')}
              onStartActiveWorkout={(workout) => setActiveWorkoutPlayer(workout)}
            />
          )}

          {currentView === 'workouts' && (
            <WorkoutsView
              workouts={workouts}
              onStartActiveWorkout={(workout) => setActiveWorkoutPlayer(workout)}
              onAddCustomWorkout={handleAddCustomWorkout}
            />
          )}

          {currentView === 'nutrition' && (
            <NutritionView
              macros={macros}
              meals={meals}
              onAddMeal={handleAddMeal}
              onDeleteMeal={handleDeleteMeal}
            />
          )}

          {currentView === 'recovery' && (
            <RecoveryView
              sleepLogs={sleepLogs}
              onAddSleepLog={handleAddSleepLog}
            />
          )}

          {currentView === 'progress' && (
            <ProgressView
              personalRecords={personalRecords}
              onAddPR={handleAddPR}
            />
          )}

          {currentView === 'trainers' && (
            <TrainersView
              trainers={initialTrainers}
            />
          )}

          {currentView === 'landing' && (
            <LandingView
              onSelectView={setCurrentView}
              onOpenAuth={() => setCurrentView('dashboard')}
            />
          )}

          {currentView === 'settings' && (
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 space-y-6">
              <h2 className="text-2xl font-black text-slate-100">App Preferences & Biometrics</h2>
              <div className="space-y-4 text-xs text-slate-300">
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 flex justify-between items-center">
                  <div>
                    <p className="font-bold text-slate-100">Gemini AI Auto-Optimization</p>
                    <p className="text-slate-400">Automatically adjust workouts based on sleep and HRV logs.</p>
                  </div>
                  <span className="text-emerald-400 font-bold bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">Enabled</span>
                </div>
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 flex justify-between items-center">
                  <div>
                    <p className="font-bold text-slate-100">Sync Apple Health / Wearables</p>
                    <p className="text-slate-400">Continuous step and heart rate ingestion active.</p>
                  </div>
                  <span className="text-cyan-400 font-bold bg-cyan-500/10 px-3 py-1 rounded-full border border-cyan-500/20">Connected</span>
                </div>
              </div>
            </div>
          )}
        </main>

        {/* Global Footer */}
        <Footer onSelectView={setCurrentView} />
      </div>

      {/* Interactive Workout Player Modal */}
      {activeWorkoutPlayer && (
        <ActiveWorkoutModal
          workout={activeWorkoutPlayer}
          onClose={() => setActiveWorkoutPlayer(null)}
          onComplete={() => {
            setTodayWorkoutCompleted(true);
            setUser((prev) => ({ ...prev, streakDays: prev.streakDays + 1 }));
          }}
        />
      )}

      {/* Floating AI Coach Drawer */}
      <AICoachDrawer
        isOpen={showAICoach}
        onClose={() => setShowAICoach(false)}
      />
    </div>
  );
}
