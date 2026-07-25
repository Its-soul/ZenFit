import React, { useState } from 'react';
import { 
  Sparkles, 
  Dumbbell, 
  HeartPulse, 
  UtensilsCrossed, 
  CheckCircle2, 
  ArrowRight, 
  Play, 
  Star, 
  ShieldCheck, 
  Activity,
  X
} from 'lucide-react';
import { ViewMode } from '../types';

interface LandingViewProps {
  onSelectView: (view: ViewMode) => void;
  onOpenAuth: () => void;
}

export const LandingView: React.FC<LandingViewProps> = ({ onSelectView, onOpenAuth }) => {
  const [showVideoModal, setShowVideoModal] = useState(false);

  return (
    <div className="space-y-12 pb-16 animate-fade-in">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-slate-900/90 border border-slate-800/80 p-8 md:p-16 text-center shadow-2xl">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-tr from-emerald-500/10 via-teal-500/10 to-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl mx-auto space-y-6">
          {/* Floating Pill */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold tracking-wide uppercase">
            <Sparkles className="w-4 h-4" />
            <span>Adaptive Fitness AI Engine</span>
          </div>

          {/* Headline */}
          <h1 className="text-3xl md:text-5xl font-black text-slate-100 tracking-tight leading-tight">
            Fitness guidance that adapts to your <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">real life</span>.
          </h1>

          <p className="text-sm md:text-base text-slate-300 leading-relaxed max-w-2xl mx-auto">
            ZenFit Elite combines real-time HRV recovery analytics, Gemini AI personalized workouts, and computer vision macro scanning into one high-performance dashboard.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <button
              onClick={() => onSelectView('dashboard')}
              className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-gradient-to-r from-emerald-400 via-teal-400 to-emerald-500 hover:from-emerald-300 hover:to-teal-400 text-slate-950 font-black text-sm shadow-xl shadow-emerald-500/25 transition-all hover:scale-[1.03] active:scale-[0.98] flex items-center justify-center gap-2"
            >
              <span>Build My Plan Now</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => setShowVideoModal(true)}
              className="w-full sm:w-auto px-6 py-4 rounded-2xl bg-slate-950/80 hover:bg-slate-800 text-slate-200 border border-slate-700 font-bold text-sm transition-all flex items-center justify-center gap-2"
            >
              <Play className="w-4 h-4 fill-slate-200" />
              <span>How It Works</span>
            </button>
          </div>
        </div>
      </section>

      {/* 3 Core Feature Cards */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl space-y-4 hover:border-emerald-500/40 transition-all group">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center group-hover:scale-110 transition-transform">
            <Dumbbell className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-100">Personalized Workouts</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            AI generated routines tailored to your specific equipment, target muscle group, and daily fatigue scores.
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl space-y-4 hover:border-teal-500/40 transition-all group">
          <div className="w-12 h-12 rounded-2xl bg-teal-500/10 border border-teal-500/20 text-teal-400 flex items-center justify-center group-hover:scale-110 transition-transform">
            <HeartPulse className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-100">HRV Recovery Tracking</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Real-time biometric analysis calculates your central nervous system readiness before every workout.
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-xl space-y-4 hover:border-cyan-500/40 transition-all group">
          <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center group-hover:scale-110 transition-transform">
            <UtensilsCrossed className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-100">AI Vision Macro Scanner</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Snap a photo of any dish to automatically calculate protein, carbohydrates, fats, and total caloric intake.
          </p>
        </div>
      </section>

      {/* Social Proof Stats Banner */}
      <section className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-8 shadow-xl">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div className="space-y-1">
            <p className="text-3xl md:text-4xl font-black text-slate-100">500k+</p>
            <p className="text-xs text-slate-400 font-medium">Active Athletes</p>
          </div>
          <div className="space-y-1">
            <p className="text-3xl md:text-4xl font-black text-emerald-400">12M+</p>
            <p className="text-xs text-slate-400 font-medium">Workouts Logged</p>
          </div>
          <div className="space-y-1">
            <p className="text-3xl md:text-4xl font-black text-slate-100">94%</p>
            <p className="text-xs text-slate-400 font-medium">Goal Success Rate</p>
          </div>
          <div className="space-y-1">
            <p className="text-3xl md:text-4xl font-black text-amber-400 flex items-center justify-center gap-1">
              <span>4.9</span>
              <Star className="w-5 h-5 fill-amber-400" />
            </p>
            <p className="text-xs text-slate-400 font-medium">Global App Rating</p>
          </div>
        </div>
      </section>

      {/* How it Works Modal */}
      {showVideoModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-xl w-full p-6 space-y-4 shadow-2xl relative animate-fade-in">
            <button
              onClick={() => setShowVideoModal(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-200"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-xl font-black text-slate-100">How ZenFit Elite Works</h3>
            <div className="aspect-video bg-slate-950 rounded-2xl flex flex-col items-center justify-center p-6 border border-slate-800 text-center space-y-3">
              <div className="w-14 h-14 rounded-full bg-emerald-400/20 border border-emerald-400/30 text-emerald-400 flex items-center justify-center">
                <Play className="w-6 h-6 fill-emerald-400 ml-1" />
              </div>
              <p className="text-xs text-slate-300 font-bold">Interactive Platform Walkthrough Active</p>
              <p className="text-[11px] text-slate-500 max-w-sm">
                ZenFit continuously syncs your HRV, daily sleep logs, and meal macros to refine workout volume automatically.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
