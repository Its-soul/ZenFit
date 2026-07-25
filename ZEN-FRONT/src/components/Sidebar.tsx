import React from 'react';
import { 
  LayoutDashboard, 
  Dumbbell, 
  UtensilsCrossed, 
  HeartPulse, 
  TrendingUp, 
  Users, 
  Sparkles, 
  Play, 
  Settings, 
  HelpCircle,
  X,
  Flame
} from 'lucide-react';
import { ViewMode } from '../types';

interface SidebarProps {
  currentView: ViewMode;
  onSelectView: (view: ViewMode) => void;
  onStartWorkout: () => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
  streakDays: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentView,
  onSelectView,
  onStartWorkout,
  isOpenMobile,
  onCloseMobile,
  streakDays,
}) => {
  const navItems: { id: ViewMode; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'workouts', label: 'Training Plan', icon: Dumbbell },
    { id: 'nutrition', label: 'Meal Plan', icon: UtensilsCrossed },
    { id: 'recovery', label: 'Recovery Status', icon: HeartPulse },
    { id: 'progress', label: 'Progress & PRs', icon: TrendingUp },
    { id: 'trainers', label: 'Pro Trainers', icon: Users },
    { id: 'landing', label: 'AI Showcase', icon: Sparkles },
  ];

  const handleNavClick = (view: ViewMode) => {
    onSelectView(view);
    onCloseMobile();
  };

  return (
    <>
      {/* Backdrop for Mobile */}
      {isOpenMobile && (
        <div 
          className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={onCloseMobile}
        />
      )}

      {/* Sidebar Container */}
      <aside
        id="app-sidebar"
        className={`fixed top-0 left-0 bottom-0 w-64 bg-slate-900/90 border-r border-slate-800/80 backdrop-blur-xl z-50 flex flex-col transition-transform duration-300 lg:translate-x-0 ${
          isOpenMobile ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-6 flex items-center justify-between border-b border-slate-800/60">
          <div 
            className="flex items-center gap-3 cursor-pointer group"
            onClick={() => handleNavClick('dashboard')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-transform">
              <span className="text-slate-950 font-black text-xl tracking-tighter">Z</span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-lg font-bold text-slate-100 tracking-tight">ZenFit</span>
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">ELITE</span>
              </div>
              <p className="text-xs text-slate-400 font-medium">High-Performance Zen</p>
            </div>
          </div>

          <button
            id="close-sidebar-mobile-btn"
            onClick={onCloseMobile}
            className="p-1.5 text-slate-400 hover:text-slate-200 rounded-lg lg:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Streak Counter Badge */}
        <div className="px-6 py-3.5 mx-4 mt-4 rounded-xl bg-gradient-to-r from-amber-500/10 via-emerald-500/10 to-teal-500/10 border border-emerald-500/20 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-amber-500/20 text-amber-400">
              <Flame className="w-4 h-4 fill-amber-400/20 animate-pulse" />
            </div>
            <div>
              <p className="text-xs text-slate-400 font-medium">Streak</p>
              <p className="text-sm font-bold text-slate-100">{streakDays} Days Strong</p>
            </div>
          </div>
          <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wide">Active</span>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                id={`nav-item-${item.id}`}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-sm font-semibold transition-all relative ${
                  isActive
                    ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 shadow-sm shadow-emerald-500/5'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                {isActive && (
                  <div className="absolute left-0 top-2 bottom-2 w-1 bg-emerald-400 rounded-r-full shadow-glow" />
                )}
                <Icon className={`w-5 h-5 ${isActive ? 'text-emerald-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Start Workout Primary CTA */}
        <div className="p-4 border-t border-slate-800/60 space-y-3">
          <button
            id="sidebar-start-workout-btn"
            onClick={onStartWorkout}
            className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-bold text-slate-950 bg-gradient-to-r from-emerald-400 via-teal-400 to-emerald-500 hover:from-emerald-300 hover:to-teal-400 shadow-lg shadow-emerald-500/25 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <Play className="w-4 h-4 fill-slate-950" />
            <span>Start Workout</span>
          </button>

          <div className="pt-2 flex items-center justify-between text-xs text-slate-400 px-1">
            <button 
              onClick={() => handleNavClick('settings')}
              className="flex items-center gap-1.5 hover:text-slate-200"
            >
              <Settings className="w-3.5 h-3.5" />
              <span>Settings</span>
            </button>
            <button 
              onClick={() => alert('ZenFit Support: Contact coach@zenfit.elite or ask the AI Coach!')}
              className="flex items-center gap-1.5 hover:text-slate-200"
            >
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Help</span>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
