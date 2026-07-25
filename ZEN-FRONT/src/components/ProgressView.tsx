import React, { useState } from 'react';
import { 
  TrendingUp, 
  Award, 
  Flame, 
  Plus, 
  X, 
  CheckCircle, 
  Zap, 
  BarChart2, 
  Calendar,
  Sparkles
} from 'lucide-react';
import { PersonalRecord } from '../types';

interface ProgressViewProps {
  personalRecords: PersonalRecord[];
  onAddPR: (pr: PersonalRecord) => void;
}

export const ProgressView: React.FC<ProgressViewProps> = ({
  personalRecords,
  onAddPR,
}) => {
  const [showPRModal, setShowPRModal] = useState(false);
  const [exerciseName, setExerciseName] = useState('');
  const [prValue, setPrValue] = useState('');
  const [prCategory, setPrCategory] = useState('Strength');

  const handleSavePR = (e: React.FormEvent) => {
    e.preventDefault();
    if (!exerciseName || !prValue) return;

    const newPR: PersonalRecord = {
      id: `pr-${Date.now()}`,
      exercise: exerciseName,
      value: prValue,
      date: new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }),
      category: prCategory,
    };

    onAddPR(newPR);
    setShowPRModal(false);
    setExerciseName('');
    setPrValue('');
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800/80 p-6 md:p-8 shadow-xl">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-bold">
              <Award className="w-3.5 h-3.5" />
              <span>Athletic Milestone Tracker</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-black text-slate-100 tracking-tight">
              Progress & Personal Records
            </h2>
            <p className="text-xs md:text-sm text-slate-400 max-w-xl leading-relaxed">
              Track long-term strength achievements, cardiovascular PRs, and athletic consistency trends.
            </p>
          </div>

          <button
            id="open-add-pr-modal-btn"
            onClick={() => setShowPRModal(true)}
            className="flex items-center justify-center gap-2 px-5 py-3.5 rounded-2xl bg-amber-400 hover:bg-amber-300 text-slate-950 font-bold text-xs md:text-sm shadow-xl shadow-amber-500/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <Plus className="w-4 h-4" />
            <span>Add Personal Record (PR)</span>
          </button>
        </div>
      </div>

      {/* Metrics Summary Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400">Consistency Outlook</span>
            <span className="text-emerald-400 font-bold text-xs bg-emerald-500/10 px-2 py-0.5 rounded-full">Building</span>
          </div>
          <p className="text-3xl font-black text-slate-100">14 Days</p>
          <p className="text-xs text-slate-400">92% workout adherence over last 30 days.</p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400">Strength Volume</span>
            <span className="text-cyan-400 font-bold text-xs bg-cyan-500/10 px-2 py-0.5 rounded-full">+14.2%</span>
          </div>
          <p className="text-3xl font-black text-slate-100">42,800 kg</p>
          <p className="text-xs text-slate-400">Cumulative tonnage lifted this month.</p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400">VO2 Max Estimate</span>
            <span className="text-amber-400 font-bold text-xs bg-amber-500/10 px-2 py-0.5 rounded-full">Superior</span>
          </div>
          <p className="text-3xl font-black text-slate-100">54 ml/kg/min</p>
          <p className="text-xs text-slate-400">Top 5% for your age bracket.</p>
        </div>
      </div>

      {/* PR Ledger Grid */}
      <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-100">Hall of Personal Records</h3>
            <p className="text-xs text-slate-400">Verified peak performances across all disciplines.</p>
          </div>
          <span className="text-xs font-mono text-amber-400 font-bold">{personalRecords.length} PRs Logged</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {personalRecords.map((pr) => (
            <div
              key={pr.id}
              className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 hover:border-amber-500/40 transition-all flex items-center justify-between group"
            >
              <div className="flex items-center gap-3">
                <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400">
                  <Award className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-slate-100 group-hover:text-amber-300 transition-colors">
                    {pr.exercise}
                  </h4>
                  <div className="flex items-center gap-2 text-[10px] text-slate-400 mt-0.5">
                    <span className="bg-slate-900 px-2 py-0.5 rounded text-slate-300 font-semibold">{pr.category}</span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3 text-slate-500" />
                      {pr.date}
                    </span>
                  </div>
                </div>
              </div>

              <div className="text-right">
                <span className="text-base font-black text-amber-400 font-mono block">{pr.value}</span>
                <span className="text-[10px] uppercase font-bold text-emerald-400">Verified</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* PR Modal */}
      {showPRModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-md w-full p-6 space-y-6 shadow-2xl relative animate-fade-in">
            <button
              onClick={() => setShowPRModal(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-200"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="space-y-1">
              <h3 className="text-xl font-black text-slate-100">Log Personal Record</h3>
              <p className="text-xs text-slate-400">Add a new peak lift or timed event milestone.</p>
            </div>

            <form onSubmit={handleSavePR} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">Exercise / Movement</label>
                <input
                  type="text"
                  value={exerciseName}
                  onChange={(e) => setExerciseName(e.target.value)}
                  placeholder="e.g. Overhead Press, 10km Run"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">Record Value</label>
                <input
                  type="text"
                  value={prValue}
                  onChange={(e) => setPrValue(e.target.value)}
                  placeholder="e.g. 90 kg (198 lbs) or 42m 15s"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">Category</label>
                <select
                  value={prCategory}
                  onChange={(e) => setPrCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                >
                  <option value="Strength">Strength</option>
                  <option value="Cardio">Cardio & Running</option>
                  <option value="Olympic">Olympic Weightlifting</option>
                  <option value="Mobility">Mobility & Bodyweight</option>
                </select>
              </div>

              <button
                type="submit"
                className="w-full py-3 px-4 rounded-xl font-bold text-xs bg-amber-400 hover:bg-amber-300 text-slate-950 transition-all flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20"
              >
                <Award className="w-4 h-4" />
                <span>Save Record</span>
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
