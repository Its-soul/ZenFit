import React, { useState } from 'react';
import { 
  HeartPulse, 
  Moon, 
  Activity, 
  Zap, 
  Smile, 
  Meh, 
  Frown, 
  Sparkles, 
  Clock, 
  Plus, 
  Check, 
  ArrowUp,
  ShieldCheck
} from 'lucide-react';
import { SleepLog } from '../types';

interface RecoveryViewProps {
  sleepLogs: SleepLog[];
  onAddSleepLog: (log: SleepLog) => void;
}

export const RecoveryView: React.FC<RecoveryViewProps> = ({
  sleepLogs,
  onAddSleepLog,
}) => {
  const [selectedFeeling, setSelectedFeeling] = useState<'Drained' | 'Okay' | 'Focused' | 'Strong' | 'Motivated'>('Strong');
  const [showLogSleepModal, setShowLogSleepModal] = useState(false);

  // Sleep Logger Form
  const [hours, setHours] = useState(8.0);
  const [quality, setQuality] = useState(90);
  const [hrv, setHrv] = useState(68);

  const feelings: { id: 'Drained' | 'Okay' | 'Focused' | 'Strong' | 'Motivated'; label: string; icon: any }[] = [
    { id: 'Drained', label: 'Drained', icon: Frown },
    { id: 'Okay', label: 'Okay', icon: Meh },
    { id: 'Focused', label: 'Focused', icon: Smile },
    { id: 'Strong', label: 'Strong', icon: Zap },
    { id: 'Motivated', label: 'Motivated', icon: Sparkles },
  ];

  const handleSaveSleep = (e: React.FormEvent) => {
    e.preventDefault();
    const newLog: SleepLog = {
      id: `sl-${Date.now()}`,
      date: 'Today',
      hoursSlept: hours,
      qualityPercentage: quality,
      hrvMs: hrv,
      restingHeartRate: 52,
      feeling: selectedFeeling,
    };
    onAddSleepLog(newLog);
    setShowLogSleepModal(false);
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800/80 p-6 md:p-8 shadow-xl">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-80 h-80 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/10 border border-teal-500/20 text-teal-400 text-xs font-bold">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Parasympathetic System Check</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-black text-slate-100 tracking-tight">
              Recovery & HRV Intelligence
            </h2>
            <p className="text-xs md:text-sm text-slate-400 max-w-xl leading-relaxed">
              Understand what your nervous system and muscle fibers need today before hitting maximum exertion.
            </p>
          </div>

          <button
            id="open-log-sleep-modal-btn"
            onClick={() => setShowLogSleepModal(true)}
            className="flex items-center justify-center gap-2 px-5 py-3.5 rounded-2xl bg-teal-400 hover:bg-teal-300 text-slate-950 font-bold text-xs md:text-sm shadow-xl shadow-teal-500/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <Moon className="w-4 h-4 fill-slate-950" />
            <span>Log Last Night's Sleep</span>
          </button>
        </div>
      </div>

      {/* Main Score & Biometrics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* Left: 85% Radial Gauge */}
        <div className="lg:col-span-5 bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl flex flex-col items-center justify-between text-center space-y-6">
          <div className="w-full text-left">
            <span className="text-xs font-bold uppercase tracking-wider text-teal-400 bg-teal-500/10 px-2.5 py-1 rounded-lg border border-teal-500/20">
              Readiness Score
            </span>
            <h3 className="text-lg font-bold text-slate-100 mt-2">85% Recovered Today</h3>
            <p className="text-xs text-slate-400">Prime athletic window for high-load strength or Zone 2 cardio.</p>
          </div>

          {/* Radial Gauge Visual */}
          <div className="relative my-2">
            <div className="absolute inset-0 bg-teal-500/20 rounded-full blur-2xl animate-pulse" />
            <svg className="w-48 h-48 transform -rotate-90 relative z-10" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="42" stroke="#1e293b" strokeWidth="8" fill="transparent" />
              <circle
                cx="50"
                cy="50"
                r="42"
                stroke="#10b981"
                strokeWidth="8"
                strokeDasharray={263.8}
                strokeDashoffset={263.8 - (263.8 * 85) / 100}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-1000"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center z-20 pointer-events-none">
              <span className="text-3xl font-black text-slate-100">85%</span>
              <span className="text-[10px] uppercase font-bold text-emerald-400">HIGH PRIME</span>
            </div>
          </div>

          {/* Biometric Pills */}
          <div className="grid grid-cols-3 gap-2 w-full pt-2">
            <div className="bg-slate-950/60 p-2.5 rounded-2xl border border-slate-800/80 text-left">
              <span className="text-[10px] text-slate-400 block">HRV</span>
              <span className="text-sm font-bold text-emerald-400">68 ms</span>
            </div>
            <div className="bg-slate-950/60 p-2.5 rounded-2xl border border-slate-800/80 text-left">
              <span className="text-[10px] text-slate-400 block">Rest HR</span>
              <span className="text-sm font-bold text-slate-200">52 bpm</span>
            </div>
            <div className="bg-slate-950/60 p-2.5 rounded-2xl border border-slate-800/80 text-left">
              <span className="text-[10px] text-slate-400 block">Temp Delta</span>
              <span className="text-sm font-bold text-cyan-400">+0.1°C</span>
            </div>
          </div>
        </div>

        {/* Right: Daily Check-in & Feeling Buttons */}
        <div className="lg:col-span-7 bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl flex flex-col justify-between space-y-6">
          <div className="space-y-4">
            <div>
              <h3 className="text-base font-bold text-slate-100">Daily Neurological Feeling Check-in</h3>
              <p className="text-xs text-slate-400">How does your mind and body feel right now?</p>
            </div>

            {/* Feeling Selector Buttons */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              {feelings.map((f) => {
                const Icon = f.icon;
                const isSelected = selectedFeeling === f.id;
                return (
                  <button
                    key={f.id}
                    onClick={() => setSelectedFeeling(f.id)}
                    className={`p-3 rounded-2xl border flex flex-col items-center gap-2 transition-all ${
                      isSelected
                        ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40 shadow-lg shadow-emerald-500/10'
                        : 'bg-slate-950/60 text-slate-400 border-slate-800/80 hover:bg-slate-800 hover:text-slate-200'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-xs font-bold">{f.label}</span>
                  </button>
                );
              })}
            </div>

            <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 text-xs space-y-1">
              <div className="flex items-center gap-2 text-emerald-400 font-bold">
                <Sparkles className="w-4 h-4" />
                <span>AI Recovery Recommendation</span>
              </div>
              <p className="text-slate-300 leading-relaxed">
                Since you feel <strong className="text-white">{selectedFeeling}</strong> and your sleep was 8.2 hrs, prioritize your planned Strength session today. Follow up with 10 minutes of box breathing.
              </p>
            </div>
          </div>

          {/* Sleep Logs History */}
          <div className="space-y-3">
            <span className="text-xs font-bold text-slate-300 block">Recent Sleep History</span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {sleepLogs.slice(0, 4).map((log) => (
                <div key={log.id} className="p-3 rounded-2xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between text-xs">
                  <div className="space-y-0.5">
                    <span className="font-bold text-slate-200">{log.date}</span>
                    <p className="text-[10px] text-slate-400">{log.hoursSlept} hrs ({log.qualityPercentage}% Quality)</p>
                  </div>
                  <span className="px-2 py-0.5 rounded-lg bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/20">
                    {log.hrvMs}ms HRV
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

      {/* Log Sleep Modal */}
      {showLogSleepModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-md w-full p-6 space-y-6 shadow-2xl relative animate-fade-in">
            <div className="space-y-1">
              <h3 className="text-xl font-black text-slate-100">Log Sleep Session</h3>
              <p className="text-xs text-slate-400">Record last night's sleep biometrics for recovery syncing.</p>
            </div>

            <form onSubmit={handleSaveSleep} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">
                  Hours Slept: <span className="text-teal-400">{hours} hrs</span>
                </label>
                <input
                  type="range"
                  min="4.0"
                  max="12.0"
                  step="0.5"
                  value={hours}
                  onChange={(e) => setHours(parseFloat(e.target.value))}
                  className="w-full accent-teal-400 cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">
                  Sleep Quality Rating: <span className="text-teal-400">{quality}%</span>
                </label>
                <input
                  type="range"
                  min="30"
                  max="100"
                  step="5"
                  value={quality}
                  onChange={(e) => setQuality(parseInt(e.target.value))}
                  className="w-full accent-teal-400 cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-300 mb-1">HRV Value (ms)</label>
                <input
                  type="number"
                  value={hrv}
                  onChange={(e) => setHrv(parseInt(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                />
              </div>

              <div className="flex items-center gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowLogSleepModal(false)}
                  className="flex-1 py-2.5 rounded-xl border border-slate-800 text-xs font-bold text-slate-400 hover:text-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 rounded-xl bg-teal-400 hover:bg-teal-300 text-slate-950 font-bold text-xs shadow-lg shadow-teal-500/20"
                >
                  Save Sleep Biometrics
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
