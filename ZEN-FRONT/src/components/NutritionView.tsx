import React, { useState } from 'react';
import { 
  UtensilsCrossed, 
  Sparkles, 
  Plus, 
  Flame, 
  Camera, 
  Trash2, 
  CheckCircle2, 
  X, 
  Lightbulb,
  Apple
} from 'lucide-react';
import { MealItem, NutritionMacroSummary } from '../types';

interface NutritionViewProps {
  macros: NutritionMacroSummary;
  meals: MealItem[];
  onAddMeal: (meal: MealItem) => void;
  onDeleteMeal: (mealId: string) => void;
}

export const NutritionView: React.FC<NutritionViewProps> = ({
  macros,
  meals,
  onAddMeal,
  onDeleteMeal,
}) => {
  const [showMealModal, setShowMealModal] = useState(false);
  const [mealText, setMealText] = useState('');
  const [mealType, setMealType] = useState<'Breakfast' | 'Lunch' | 'Dinner' | 'Snacks'>('Lunch');
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Manual fallback inputs
  const [manualName, setManualName] = useState('');
  const [manualCal, setManualCal] = useState('');
  const [manualProtein, setManualProtein] = useState('');
  const [manualCarbs, setManualCarbs] = useState('');
  const [manualFat, setManualFat] = useState('');

  const [activeTab, setActiveTab] = useState<'ai' | 'manual'>('ai');

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleAnalyzeAndAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAnalyzing(true);

    try {
      const res = await fetch('/api/ai/analyze-meal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mealDescription: mealText,
          imageBase64: imagePreview,
        }),
      });

      const data = await res.json();

      const newMeal: MealItem = {
        id: `meal-${Date.now()}`,
        type: mealType,
        name: data.mealName || mealText || 'Custom Healthy Dish',
        calories: Number(data.calories) || 450,
        proteinG: Number(data.protein) || 30,
        carbsG: Number(data.carbs) || 40,
        fatG: Number(data.fats) || 15,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        insight: data.insight || 'High quality protein content for optimal muscular recovery.',
      };

      onAddMeal(newMeal);
      setShowMealModal(false);
      setMealText('');
      setImagePreview(null);
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleManualAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualName) return;

    const newMeal: MealItem = {
      id: `meal-${Date.now()}`,
      type: mealType,
      name: manualName,
      calories: Number(manualCal) || 300,
      proteinG: Number(manualProtein) || 20,
      carbsG: Number(manualCarbs) || 30,
      fatG: Number(manualFat) || 10,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    onAddMeal(newMeal);
    setShowMealModal(false);
    setManualName('');
    setManualCal('');
    setManualProtein('');
    setManualCarbs('');
    setManualFat('');
  };

  const mealCategories: ('Breakfast' | 'Lunch' | 'Dinner' | 'Snacks')[] = ['Breakfast', 'Lunch', 'Dinner', 'Snacks'];

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Nutrition Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800/80 p-6 md:p-8 shadow-xl">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-bold">
              <Apple className="w-3.5 h-3.5" />
              <span>Precision Nutrient Timing</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-black text-slate-100 tracking-tight">
              Nutrition & Macro Intelligence
            </h2>
            <p className="text-xs md:text-sm text-slate-400 max-w-xl leading-relaxed">
              Log meals instantly using Gemini AI photo recognition or manual inputs to align your macro targets.
            </p>
          </div>

          <button
            id="open-nutrition-meal-modal-btn"
            onClick={() => setShowMealModal(true)}
            className="flex items-center justify-center gap-2 px-5 py-3.5 rounded-2xl bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-bold text-xs md:text-sm shadow-xl shadow-cyan-500/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <Plus className="w-4 h-4" />
            <span>Log Meal with AI</span>
          </button>
        </div>
      </div>

      {/* Macro Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Protein Card */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-5 shadow-lg space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="font-bold text-slate-300">Protein Target</span>
            <span className="text-emerald-400 font-bold">{Math.round((macros.proteinCurrentG / macros.proteinGoalG) * 100)}%</span>
          </div>
          <p className="text-2xl font-black text-slate-100">
            {macros.proteinCurrentG}g <span className="text-xs text-slate-500 font-normal">/ {macros.proteinGoalG}g</span>
          </p>
          <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
            <div style={{ width: `${Math.min(100, (macros.proteinCurrentG / macros.proteinGoalG) * 100)}%` }} className="h-full bg-emerald-400 rounded-full" />
          </div>
        </div>

        {/* Carbs Card */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-5 shadow-lg space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="font-bold text-slate-300">Carbohydrates</span>
            <span className="text-cyan-400 font-bold">{Math.round((macros.carbsCurrentG / macros.carbsGoalG) * 100)}%</span>
          </div>
          <p className="text-2xl font-black text-slate-100">
            {macros.carbsCurrentG}g <span className="text-xs text-slate-500 font-normal">/ {macros.carbsGoalG}g</span>
          </p>
          <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
            <div style={{ width: `${Math.min(100, (macros.carbsCurrentG / macros.carbsGoalG) * 100)}%` }} className="h-full bg-cyan-400 rounded-full" />
          </div>
        </div>

        {/* Fats Card */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-2xl p-5 shadow-lg space-y-2">
          <div className="flex justify-between items-center text-xs">
            <span className="font-bold text-slate-300">Healthy Fats</span>
            <span className="text-amber-400 font-bold">{Math.round((macros.fatCurrentG / macros.fatGoalG) * 100)}%</span>
          </div>
          <p className="text-2xl font-black text-slate-100">
            {macros.fatCurrentG}g <span className="text-xs text-slate-500 font-normal">/ {macros.fatGoalG}g</span>
          </p>
          <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
            <div style={{ width: `${Math.min(100, (macros.fatCurrentG / macros.fatGoalG) * 100)}%` }} className="h-full bg-amber-400 rounded-full" />
          </div>
        </div>
      </div>

      {/* Meal Logs Categorized Accordion */}
      <div className="space-y-6">
        {mealCategories.map((category) => {
          const categoryMeals = meals.filter((m) => m.type === category);
          const categoryCalories = categoryMeals.reduce((sum, m) => sum + m.calories, 0);

          return (
            <div key={category} className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-slate-800 text-cyan-400">
                    <UtensilsCrossed className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-100">{category}</h3>
                    <p className="text-xs text-slate-400">{categoryMeals.length} items logged</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono font-bold text-slate-300 bg-slate-950 px-3 py-1 rounded-xl border border-slate-800">
                    {categoryCalories} kcal
                  </span>
                  <button
                    onClick={() => { setMealType(category); setShowMealModal(true); }}
                    className="p-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200"
                    title={`Add ${category}`}
                  >
                    <Plus className="w-4 h-4 text-cyan-400" />
                  </button>
                </div>
              </div>

              {categoryMeals.length === 0 ? (
                <p className="text-xs text-slate-500 italic py-2">No items logged yet for {category}.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {categoryMeals.map((meal) => (
                    <div
                      key={meal.id}
                      className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 hover:border-cyan-500/30 transition-all flex flex-col justify-between space-y-2 group"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <h4 className="text-sm font-bold text-slate-100 group-hover:text-cyan-300 transition-colors">
                            {meal.name}
                          </h4>
                          <span className="text-[10px] text-slate-500 font-mono">{meal.time}</span>
                        </div>
                        <button
                          onClick={() => onDeleteMeal(meal.id)}
                          className="text-slate-500 hover:text-rose-400 p-1"
                          title="Delete meal"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      {/* Macros Chips */}
                      <div className="flex items-center gap-2 text-[11px] font-mono">
                        <span className="bg-slate-900 px-2 py-0.5 rounded text-slate-300">
                          {meal.calories} kcal
                        </span>
                        <span className="bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded">
                          {meal.proteinG}g P
                        </span>
                        <span className="bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded">
                          {meal.carbsG}g C
                        </span>
                        <span className="bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded">
                          {meal.fatG}g F
                        </span>
                      </div>

                      {meal.insight && (
                        <p className="text-[10px] text-slate-400 bg-slate-900/80 p-2 rounded-xl border border-slate-800 flex items-start gap-1.5">
                          <Lightbulb className="w-3 h-3 text-cyan-400 flex-shrink-0 mt-0.5" />
                          <span>{meal.insight}</span>
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Meal Logger & AI Scanner Modal */}
      {showMealModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full p-6 space-y-6 shadow-2xl relative animate-fade-in">
            <button
              onClick={() => setShowMealModal(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-200"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="space-y-1">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-bold border border-cyan-500/20">
                <Sparkles className="w-3.5 h-3.5" />
                <span>AI Vision & Nutrition Engine</span>
              </div>
              <h3 className="text-xl font-black text-slate-100">Log Nutrition Item</h3>
              <p className="text-xs text-slate-400">Describe or upload a meal photo for auto-calculated macros.</p>
            </div>

            {/* Mode Switcher */}
            <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800">
              <button
                type="button"
                onClick={() => setActiveTab('ai')}
                className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
                  activeTab === 'ai' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'text-slate-400'
                }`}
              >
                AI Auto-Scan
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('manual')}
                className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${
                  activeTab === 'manual' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'text-slate-400'
                }`}
              >
                Manual Entry
              </button>
            </div>

            {activeTab === 'ai' ? (
              <form onSubmit={handleAnalyzeAndAdd} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Meal Category</label>
                  <select
                    value={mealType}
                    onChange={(e) => setMealType(e.target.value as any)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="Breakfast">Breakfast</option>
                    <option value="Lunch">Lunch</option>
                    <option value="Dinner">Dinner</option>
                    <option value="Snacks">Snacks</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Meal Description</label>
                  <textarea
                    rows={3}
                    value={mealText}
                    onChange={(e) => setMealText(e.target.value)}
                    placeholder="e.g. 2 eggs scrambled with spinach, whole wheat toast with avocado, black coffee"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                  />
                </div>

                {/* Photo Upload Zone */}
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Optional Meal Photo</label>
                  <div className="border-2 border-dashed border-slate-800 hover:border-cyan-500/50 rounded-2xl p-4 text-center cursor-pointer transition-colors relative bg-slate-950/50">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="absolute inset-0 opacity-0 cursor-pointer"
                    />
                    {imagePreview ? (
                      <div className="space-y-2">
                        <img src={imagePreview} alt="Meal Preview" className="h-28 mx-auto rounded-xl object-cover" />
                        <span className="text-[10px] text-cyan-400 font-bold block">Photo attached! Click to change</span>
                      </div>
                    ) : (
                      <div className="space-y-1 py-2">
                        <Camera className="w-6 h-6 text-slate-500 mx-auto" />
                        <p className="text-xs text-slate-300 font-medium">Click to upload meal photo</p>
                        <p className="text-[10px] text-slate-500">Supports PNG, JPG, WebP</p>
                      </div>
                    )}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isAnalyzing}
                  className="w-full py-3 px-4 rounded-xl font-bold text-xs bg-cyan-400 hover:bg-cyan-300 text-slate-950 transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 disabled:opacity-50"
                >
                  {isAnalyzing ? (
                    <>
                      <Sparkles className="w-4 h-4 animate-spin" />
                      <span>Analyzing Nutrition with Gemini...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Analyze & Log Meal</span>
                    </>
                  )}
                </button>
              </form>
            ) : (
              <form onSubmit={handleManualAdd} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-300 mb-1">Dish Name</label>
                  <input
                    type="text"
                    value={manualName}
                    onChange={(e) => setManualName(e.target.value)}
                    placeholder="e.g. Chicken Rice Bowl"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1">Calories (kcal)</label>
                    <input
                      type="number"
                      value={manualCal}
                      onChange={(e) => setManualCal(e.target.value)}
                      placeholder="500"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1">Protein (g)</label>
                    <input
                      type="number"
                      value={manualProtein}
                      onChange={(e) => setManualProtein(e.target.value)}
                      placeholder="35"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1">Carbs (g)</label>
                    <input
                      type="number"
                      value={manualCarbs}
                      onChange={(e) => setManualCarbs(e.target.value)}
                      placeholder="45"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-300 mb-1">Fats (g)</label>
                    <input
                      type="number"
                      value={manualFat}
                      onChange={(e) => setManualFat(e.target.value)}
                      placeholder="15"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 px-4 rounded-xl font-bold text-xs bg-slate-100 hover:bg-white text-slate-950 transition-all flex items-center justify-center gap-2"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Save Manual Entry</span>
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
