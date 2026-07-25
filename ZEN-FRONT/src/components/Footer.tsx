import React from 'react';
import { ViewMode } from '../types';

interface FooterProps {
  onSelectView: (view: ViewMode) => void;
}

export const Footer: React.FC<FooterProps> = ({ onSelectView }) => {
  return (
    <footer className="mt-16 border-t border-slate-800/80 bg-slate-950/80 pt-12 pb-8 px-4 lg:px-8 text-xs text-slate-400">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
        {/* Brand Column */}
        <div className="space-y-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center text-slate-950 font-black text-lg">
              Z
            </div>
            <span className="text-base font-bold text-slate-100">ZenFit Elite</span>
          </div>
          <p className="text-slate-400 text-xs leading-relaxed">
            High-Performance Zen. Adaptive workouts, HRV recovery analytics, and macro tracking backed by sports science.
          </p>
        </div>

        {/* Platform Links */}
        <div className="space-y-2">
          <h4 className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">Platform</h4>
          <ul className="space-y-1.5">
            <li><button onClick={() => onSelectView('dashboard')} className="hover:text-emerald-400">Dashboard</button></li>
            <li><button onClick={() => onSelectView('workouts')} className="hover:text-emerald-400">Training Library</button></li>
            <li><button onClick={() => onSelectView('nutrition')} className="hover:text-emerald-400">Meal Plan & AI Scan</button></li>
            <li><button onClick={() => onSelectView('recovery')} className="hover:text-emerald-400">Recovery & HRV</button></li>
          </ul>
        </div>

        {/* Pro Services */}
        <div className="space-y-2">
          <h4 className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">Pro Services</h4>
          <ul className="space-y-1.5">
            <li><button onClick={() => onSelectView('trainers')} className="hover:text-emerald-400">Master Trainers</button></li>
            <li><button onClick={() => onSelectView('progress')} className="hover:text-emerald-400">Personal Records (PRs)</button></li>
            <li><button onClick={() => onSelectView('landing')} className="hover:text-emerald-400">AI Showcase</button></li>
          </ul>
        </div>

        {/* Newsletter */}
        <div className="space-y-3">
          <h4 className="font-bold text-slate-200 uppercase tracking-wider text-[11px]">Sports Science Digest</h4>
          <p className="text-[11px] text-slate-400">Receive weekly biometrics and hypertrophy insights.</p>
          <div className="flex gap-2">
            <input
              type="email"
              placeholder="athlete@domain.com"
              className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500 flex-1"
            />
            <button className="px-3 py-1.5 rounded-xl bg-emerald-400 hover:bg-emerald-300 text-slate-950 font-bold text-xs">
              Subscribe
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto border-t border-slate-800/60 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-500">
        <p>© {new Date().getFullYear()} ZenFit Elite Inc. All rights reserved.</p>
        <div className="flex items-center gap-4">
          <a href="#" className="hover:text-slate-300">Privacy Policy</a>
          <a href="#" className="hover:text-slate-300">Terms of Service</a>
          <a href="#" className="hover:text-slate-300">Security & Biometrics</a>
        </div>
      </div>
    </footer>
  );
};
