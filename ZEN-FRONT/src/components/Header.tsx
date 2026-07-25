import React, { useState } from 'react';
import { 
  Menu, 
  Search, 
  Bell, 
  Sparkles, 
  ChevronDown, 
  CheckCircle2, 
  X,
  Flame,
  Award
} from 'lucide-react';
import { UserProfile, ViewMode } from '../types';

interface HeaderProps {
  user: UserProfile;
  currentView: ViewMode;
  onOpenMobileSidebar: () => void;
  onToggleAICoach: () => void;
  onSelectView: (view: ViewMode) => void;
}

export const Header: React.FC<HeaderProps> = ({
  user,
  currentView,
  onOpenMobileSidebar,
  onToggleAICoach,
  onSelectView,
}) => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const notifications = [
    { id: 1, title: 'High Recovery Score', desc: '85% HRV recovery detected today. Optimal for heavy lifts!', time: '10m ago', unread: true },
    { id: 2, title: 'Workout Completed', desc: 'Full Body Strength logged (+420 kcal burned)', time: 'Yesterday', unread: false },
    { id: 3, title: 'New Trainer Available', desc: 'Dr. Sarah Lin added a new Nutrition Masterclass', time: '2 days ago', unread: false },
  ];

  const viewTitles: Record<ViewMode, string> = {
    dashboard: 'Daily Overview',
    workouts: 'Training Library',
    nutrition: 'Nutrition & Macros',
    recovery: 'Recovery & HRV',
    progress: 'Analytics & PRs',
    trainers: 'Elite Trainers',
    landing: 'AI Platform Showcase',
    settings: 'App Settings',
  };

  return (
    <header className="sticky top-0 z-30 w-full bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80 px-4 lg:px-8 py-3.5 flex items-center justify-between gap-4">
      {/* Left: Mobile Menu Trigger & View Title */}
      <div className="flex items-center gap-3">
        <button
          id="mobile-sidebar-toggle-btn"
          onClick={onOpenMobileSidebar}
          className="p-2 rounded-xl text-slate-300 hover:text-white bg-slate-900 border border-slate-800 lg:hidden"
          aria-label="Open sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <h1 className="text-xl font-black text-slate-100 tracking-tight flex items-center gap-2">
            {viewTitles[currentView]}
            {currentView === 'dashboard' && (
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Live Stats
              </span>
            )}
          </h1>
          <p className="text-xs text-slate-400 hidden sm:block">
            Welcome back, <span className="text-slate-200 font-semibold">{user.name}</span>. Precision tracking active.
          </p>
        </div>
      </div>

      {/* Middle: Search Input Bar */}
      <div className="hidden md:flex flex-1 max-w-md mx-4 relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          id="global-header-search-input"
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search workouts, recipes, trainers, PRs..."
          className="w-full bg-slate-900/90 border border-slate-800 focus:border-emerald-500/50 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500/50 transition-all"
        />
        {searchQuery && (
          <button 
            onClick={() => setSearchQuery('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2.5">
        {/* AI Zen Coach Toggle Button */}
        <button
          id="ai-coach-header-btn"
          onClick={onToggleAICoach}
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-gradient-to-r from-emerald-500/20 to-teal-500/20 hover:from-emerald-500/30 hover:to-teal-500/30 border border-emerald-500/30 text-emerald-300 text-xs font-bold transition-all shadow-sm"
        >
          <Sparkles className="w-3.5 h-3.5 text-emerald-400 animate-spin-slow" />
          <span className="hidden sm:inline">AI Zen Coach</span>
        </button>

        {/* Notifications Popover Trigger */}
        <div className="relative">
          <button
            id="notifications-toggle-btn"
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 rounded-xl text-slate-300 hover:text-white bg-slate-900 border border-slate-800 relative transition-colors"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-400 ring-4 ring-slate-950 animate-ping" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-emerald-400" />
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl z-50 p-4 space-y-3">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="text-sm font-bold text-slate-100">Notifications</span>
                <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full font-semibold">1 New</span>
              </div>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {notifications.map((n) => (
                  <div key={n.id} className={`p-2.5 rounded-xl text-xs space-y-1 transition-colors ${n.unread ? 'bg-slate-800/80 border border-emerald-500/20' : 'bg-slate-900/50'}`}>
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">{n.title}</span>
                      <span className="text-[10px] text-slate-500">{n.time}</span>
                    </div>
                    <p className="text-slate-400 leading-relaxed">{n.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* User Profile Pill & Dropdown */}
        <div className="relative">
          <button
            id="user-profile-menu-btn"
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="flex items-center gap-2.5 p-1.5 pr-2.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all"
          >
            <img
              src={user.avatarUrl}
              alt={user.name}
              className="w-8 h-8 rounded-lg object-cover ring-2 ring-emerald-500/30"
            />
            <div className="text-left hidden sm:block">
              <p className="text-xs font-bold text-slate-200 leading-none">{user.name}</p>
              <p className="text-[10px] text-emerald-400 font-medium leading-tight">{user.level}</p>
            </div>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {showProfileMenu && (
            <div className="absolute right-0 mt-2 w-56 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl z-50 p-2 space-y-1">
              <div className="p-2 border-b border-slate-800">
                <p className="text-xs font-bold text-slate-100">{user.name}</p>
                <p className="text-[10px] text-slate-400">{user.role}</p>
              </div>
              <button 
                onClick={() => { onSelectView('progress'); setShowProfileMenu(false); }}
                className="w-full text-left px-3 py-2 rounded-xl text-xs text-slate-300 hover:bg-slate-800 flex items-center gap-2"
              >
                <Award className="w-3.5 h-3.5 text-emerald-400" />
                <span>My Performance PRs</span>
              </button>
              <button 
                onClick={() => { onSelectView('landing'); setShowProfileMenu(false); }}
                className="w-full text-left px-3 py-2 rounded-xl text-xs text-slate-300 hover:bg-slate-800 flex items-center gap-2"
              >
                <Sparkles className="w-3.5 h-3.5 text-teal-400" />
                <span>Landing Overview</span>
              </button>
              <button 
                onClick={() => alert('ZenFit Account Settings active.')}
                className="w-full text-left px-3 py-2 rounded-xl text-xs text-slate-300 hover:bg-slate-800 flex items-center gap-2"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Account Preferences</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
