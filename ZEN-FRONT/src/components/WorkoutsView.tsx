import React, { useState } from 'react';
import { 
  Dumbbell, 
  Search, 
  Sparkles, 
  Heart, 
  Clock, 
  Flame, 
  Filter, 
  Play, 
  Plus, 
  X, 
  CheckCircle,
  Zap,
  ChevronRight
} from 'lucide-react';
import { WorkoutItem } from '../types';

interface WorkoutsViewProps {
  workouts: WorkoutItem[];
  onStartActiveWorkout: (workout: WorkoutItem) => void;
  onAddCustomWorkout: (workout: WorkoutItem) => void;
}

export const WorkoutsView: React.FC<WorkoutsViewProps> = ({
  workouts,
  onStartActiveWorkout,
  onAddCustomWorkout,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [searchFilter, setSearchFilter] = useState('');
  const [favoritesOnly, setFavoritesOnly] = useState(false);
  const [showAIGeneratorModal, setShowAIGeneratorModal] = useState(false);

  // AI Generator Form state
  const [aiGoal, setAiGoal] = useState('Hypertrophy Strength');
  const [aiDuration, setAiDuration] = useState('45 min');
  const [aiLevel, setAiLevel] = useState<'Beginner' | 'Intermediate' | 'Pro'>('Intermediate');
  const [aiEquipment, setAiEquipment] = useState('Dumbbells & Barbell');
  const [isGenerating, setIsGenerating] = useState(false);

  const categories = ['All', 'Strength', 'Yoga', 'HIIT', 'Cardio', 'Mobility'];

  const filteredWorkouts = workouts.filter((w) => {
    const matchesCategory = selectedCategory === 'All' || w.category === selectedCategory;
    const matchesSearch = w.title.toLowerCase().includes(searchFilter.toLowerCase()) || w.description.toLowerCase().includes(searchFilter.toLowerCase());
    const matchesFav = !favoritesOnly || w.isFavorite;
    return matchesCategory && matchesSearch && matchesFav;
  });

  const handleGenerateAIWorkout = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsGenerating(true);

    try {
      const res = await fetch('/api/ai/generate-workout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal: aiGoal,
          duration: aiDuration,
          level: aiLevel,
          equipment: aiEquipment,
        }),
      });

      const data = await res.json();
      
      const newWorkout: WorkoutItem = {
        id: `custom-${Date.now()}`,
        title: data.title || `${aiGoal} Custom Session`,
        category: (data.category as any) || 'Strength',
        durationMinutes: parseInt(data.duration) || 45,
        level: aiLevel,
        caloriesBurnEstimate: 450,
        imageUrl: 'https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=800&q=80',
        trainerName: 'ZenFit AI Coach',
        trainerAvatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80',
        description: data.description || 'AI tailored routine based on your fitness biometrics.',
        exercises: data.exercises || [
          { name: 'Warmup Dynamic Squats', sets: 3, reps: '12 reps', rest: '45s' },
          { name: 'Power Compound Press', sets: 4, reps: '10 reps', rest: '60s' },
          { name: 'Zen Core Plank', sets: 3, reps: '60 sec', rest: '30s' },
        ],
      };

      onAddCustomWorkout(newWorkout);
      setShowAIGeneratorModal(false);
    } catch (err) {
      console.error(err);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Workouts Hero Header */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800/80 p-6 md:p-8 shadow-xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold">
              <Zap className="w-3.5 h-3.5" />
              <span>Sports Science Verified Programs</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-black text-slate-100 tracking-tight">
              ZenFit Workout & Training Library
            </h2>
            <p className="text-xs md:text-sm text-slate-400 leading-relaxed">
              Choose from structured strength, mobility, and HIIT programs or let Gemini AI craft an adaptive custom routine.
            </p>
          </div>

          <button
            id="open-ai-workout-gen-btn"
            onClick={() => setShowAIGeneratorModal(true)}
            className="flex items-center justify-center gap-2.5 px-5 py-3.5 rounded-2xl bg-gradient-to-r from-emerald-400 via-teal-400 to-emerald-500 hover:from-emerald-300 hover:to-teal-400 text-slate-950 font-bold text-xs md:text-sm shadow-xl shadow-emerald-500/20 transition-all hover:scale-[1.02] active:scale-[0.98] self-start md:self-auto"
          >
            <Sparkles className="w-4 h-4 fill-slate-950" />
            <span>Generate AI Routine</span>
          </button>
        </div>
      </div>

      {/* Filter Bar & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-4 rounded-2xl border border-slate-800/80">
        {/* Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 md:pb-0 scrollbar-none">
          {categories.map((cat) => (
            <button
              key={cat}
              id={`workout-filter-${cat.toLowerCase()}`}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
                selectedCategory === cat
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shadow-sm'
                  : 'bg-slate-950/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search & Favorites Toggle */}
        <div className="flex items-center gap-3">
          <div className="relative flex-1 md:w-64">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              placeholder="Search library..."
              className="w-full bg-slate-950 border border-slate-800 focus:border-emerald-500/50 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none"
            />
          </div>

          <button
            onClick={() => setFavoritesOnly(!favoritesOnly)}
            className={`p-2 rounded-xl border text-xs font-bold transition-all flex items-center gap-1.5 ${
              favoritesOnly 
                ? 'bg-rose-500/20 text-rose-400 border-rose-500/30' 
                : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
            }`}
            title="Show Saved Favorites"
          >
            <Heart className={`w-4 h-4 ${favoritesOnly ? 'fill-rose-400' : ''}`} />
            <span className="hidden sm:inline">Favorites</span>
          </button>
        </div>
      </div>

      {/* Workouts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredWorkouts.map((workout) => (
          <div
            key={workout.id}
            className="group bg-slate-900/80 border border-slate-800/80 hover:border-emerald-500/40 rounded-3xl overflow-hidden shadow-xl transition-all duration-300 hover:-translate-y-1 flex flex-col justify-between"
          >
            {/* Top Image Banner */}
            <div className="relative h-48 overflow-hidden bg-slate-950">
              <img
                src={workout.imageUrl}
                alt={workout.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent" />

              {/* Category & Difficulty Badges */}
              <div className="absolute top-3 left-3 flex items-center gap-2">
                <span className="text-[10px] font-extrabold uppercase px-2.5 py-1 rounded-lg bg-slate-950/80 backdrop-blur-md text-emerald-400 border border-emerald-500/30">
                  {workout.category}
                </span>
                <span className="text-[10px] font-bold px-2 py-1 rounded-lg bg-slate-900/80 backdrop-blur-md text-slate-300 border border-slate-800">
                  {workout.level}
                </span>
              </div>

              {/* Favorite Heart Toggle */}
              <button
                className="absolute top-3 right-3 p-2 rounded-full bg-slate-950/60 backdrop-blur-md text-slate-300 hover:text-rose-400 transition-colors"
                title="Favorite"
              >
                <Heart className={`w-4 h-4 ${workout.isFavorite ? 'fill-rose-500 text-rose-500' : ''}`} />
              </button>

              {/* Duration & Calories Overlay */}
              <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between text-xs text-slate-200">
                <span className="flex items-center gap-1 bg-slate-950/80 backdrop-blur-md px-2.5 py-0.5 rounded-md border border-slate-800">
                  <Clock className="w-3.5 h-3.5 text-emerald-400" />
                  {workout.durationMinutes} min
                </span>
                <span className="flex items-center gap-1 bg-slate-950/80 backdrop-blur-md px-2.5 py-0.5 rounded-md border border-slate-800">
                  <Flame className="w-3.5 h-3.5 text-amber-400" />
                  ~{workout.caloriesBurnEstimate} kcal
                </span>
              </div>
            </div>

            {/* Workout Content */}
            <div className="p-5 space-y-3 flex-1 flex flex-col justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-100 group-hover:text-emerald-300 transition-colors line-clamp-1">
                  {workout.title}
                </h3>
                <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                  {workout.description}
                </p>
              </div>

              {/* Exercises Summary Pills */}
              <div className="space-y-1.5 pt-2 border-t border-slate-800/60">
                <span className="text-[10px] font-bold uppercase text-slate-500 tracking-wider">
                  Key Movements ({workout.exercises.length})
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {workout.exercises.slice(0, 3).map((ex, idx) => (
                    <span key={idx} className="text-[10px] bg-slate-950 px-2 py-0.5 rounded text-slate-300 border border-slate-800/80">
                      {ex.name}
                    </span>
                  ))}
                  {workout.exercises.length > 3 && (
                    <span className="text-[10px] bg-slate-950 px-1.5 py-0.5 rounded text-slate-500">
                      +{workout.exercises.length - 3} more
                    </span>
                  )}
                </div>
              </div>

              {/* Bottom Action Footer */}
              <div className="pt-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <img
                    src={workout.trainerAvatar}
                    alt={workout.trainerName}
                    className="w-6 h-6 rounded-full object-cover ring-1 ring-slate-700"
                  />
                  <span className="text-[11px] font-semibold text-slate-400">{workout.trainerName}</span>
                </div>

                <button
                  id={`start-workout-${workout.id}`}
                  onClick={() => onStartActiveWorkout(workout)}
                  className="px-4 py-2 rounded-xl bg-emerald-400 hover:bg-emerald-300 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-md shadow-emerald-500/10 transition-all"
                >
                  <Play className="w-3.5 h-3.5 fill-slate-950" />
                  <span>Start</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* AI Custom Workout Generator Modal */}
      {showAIGeneratorModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 space-y-6 shadow-2xl relative animate-fade-in">
            <button
              onClick={() => setShowAIGeneratorModal(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-200"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="space-y-1">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-bold border border-emerald-500/20">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Gemini AI Engine</span>
              </div>
              <h3 className="text-xl font-black text-slate-100">Generate Custom Training Routine</h3>
              <p className="text-xs text-slate-400">Specify your exact goals and equipment to receive a science-backed exercise plan.</p>
            </div>

            <form onSubmit={handleGenerateAIWorkout} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">Primary Goal / Focus</label>
                <input
                  type="text"
                  value={aiGoal}
                  onChange={(e) => setAiGoal(e.target.value)}
                  placeholder="e.g. Upper Body Hypertrophy, Leg Endurance, Zen Mobility"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:border-emerald-500 focus:outline-none"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Target Duration</label>
                  <select
                    value={aiDuration}
                    onChange={(e) => setAiDuration(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:border-emerald-500 focus:outline-none"
                  >
                    <option value="20 min">20 min (Express)</option>
                    <option value="35 min">35 min (Standard)</option>
                    <option value="45 min">45 min (Optimal)</option>
                    <option value="60 min">60 min (Pro Volume)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Fitness Tier</label>
                  <select
                    value={aiLevel}
                    onChange={(e) => setAiLevel(e.target.value as any)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:border-emerald-500 focus:outline-none"
                  >
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Pro">Pro Athlete</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">Available Equipment</label>
                <input
                  type="text"
                  value={aiEquipment}
                  onChange={(e) => setAiEquipment(e.target.value)}
                  placeholder="e.g. Dumbbells, Kettlebells, Pull-up bar, Bodyweight"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:border-emerald-500 focus:outline-none"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isGenerating}
                  className="w-full py-3 px-4 rounded-xl font-bold text-xs bg-emerald-400 hover:bg-emerald-300 text-slate-950 transition-all flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20 disabled:opacity-50"
                >
                  {isGenerating ? (
                    <>
                      <Sparkles className="w-4 h-4 animate-spin" />
                      <span>Synthesizing Workout with Gemini...</span>
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4" />
                      <span>Synthesize Custom Workout</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
