"use client";

import {
  BarChart3,
  Bot,
  ChevronDown,
  Dumbbell,
  HeartPulse,
  HelpCircle,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  Play,
  Salad,
  Settings,
  Sparkles,
  UserRound,
  X
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const navItems = [
  { href: "/dashboard", label: "Daily overview", icon: LayoutDashboard },
  { href: "/workouts", label: "Training plan", icon: Dumbbell },
  { href: "/nutrition", label: "Nutrition", icon: Salad },
  { href: "/recovery", label: "Recovery", icon: HeartPulse },
  { href: "/sleep", label: "Sleep", icon: Moon },
  { href: "/analytics", label: "Progress", icon: BarChart3 },
  { href: "/coach", label: "Zen coach", icon: Bot }
];

const routeTitles = {
  "/dashboard": "Daily overview",
  "/workouts": "Training plan",
  "/workouts/form-check": "Form checker",
  "/nutrition": "Nutrition and meals",
  "/nutrition/meal-analysis": "Meal analysis",
  "/recovery": "Recovery status",
  "/sleep": "Sleep and rest",
  "/analytics": "Progress and patterns",
  "/coach": "Zen coach",
  "/settings": "Settings"
};

function Brand() {
  return (
    <Link href="/dashboard" className="group flex min-w-0 items-center gap-3 rounded-xl outline-none focus-visible:ring-2 focus-visible:ring-zenSage">
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-300 to-teal-500 text-lg font-black text-slate-950 shadow-[0_10px_28px_rgba(52,211,153,0.22)] transition-transform group-hover:scale-105">
        Z
      </span>
      <span className="min-w-0">
        <span className="flex items-center gap-2">
          <span className="font-bold tracking-tight text-slate-100">ZenFit</span>
          <span className="rounded border border-emerald-400/25 bg-emerald-400/10 px-1.5 py-0.5 text-[0.625rem] font-bold uppercase tracking-wider text-emerald-300">Adaptive</span>
        </span>
        <span className="block truncate text-xs text-slate-400">Fitness that meets you here</span>
      </span>
    </Link>
  );
}

export function AppShell({ children, user, onLogout }) {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const title = routeTitles[pathname] || "ZenFit";
  const firstName = user?.full_name?.split(" ")[0] || "there";

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100">
      <a href="#main-content" className="sr-only z-[70] rounded-lg bg-emerald-300 px-4 py-2 font-semibold text-slate-950 focus:not-sr-only focus:fixed focus:left-4 focus:top-4">
        Skip to main content
      </a>

      {menuOpen ? (
        <button type="button" aria-label="Close navigation" onClick={() => setMenuOpen(false)} className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm lg:hidden" />
      ) : null}

      <aside
        id="app-navigation"
        className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-slate-800/80 bg-slate-900/95 shadow-2xl backdrop-blur-xl transition-transform duration-300 lg:translate-x-0 ${menuOpen ? "translate-x-0" : "-translate-x-full"}`}
      >
        <div className="flex items-center justify-between border-b border-slate-800/70 p-5">
          <Brand />
          <button type="button" aria-label="Close navigation" onClick={() => setMenuOpen(false)} className="icon-button lg:hidden">
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav aria-label="Main navigation" className="flex-1 space-y-1 overflow-y-auto px-4 py-5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMenuOpen(false)}
                aria-current={active ? "page" : undefined}
                className={`group relative flex min-h-12 items-center gap-3 rounded-xl border px-3.5 py-3 text-sm font-semibold outline-none transition-[background-color,border-color,color,transform] focus-visible:ring-2 focus-visible:ring-zenSage ${active ? "border-emerald-400/20 bg-emerald-400/10 text-emerald-300" : "border-transparent text-slate-400 hover:bg-slate-800/70 hover:text-slate-100"}`}
              >
                {active ? <span className="absolute inset-y-2 left-0 w-1 rounded-r-full bg-emerald-300" /> : null}
                <Icon className="h-5 w-5 shrink-0" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="space-y-3 border-t border-slate-800/70 p-4">
          <Link href="/workouts" className="flex min-h-12 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-300 via-teal-300 to-emerald-400 px-4 font-bold text-slate-950 shadow-[0_12px_30px_rgba(52,211,153,0.18)] outline-none transition-transform hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-emerald-200 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900">
            <Play className="h-4 w-4 fill-current" />
            View today&apos;s training
          </Link>
          <div className="flex items-center justify-between px-1 text-xs text-slate-400">
            <Link href="/settings" className="flex min-h-10 items-center gap-1.5 rounded-lg px-2 outline-none hover:text-slate-100 focus-visible:ring-2 focus-visible:ring-zenSage"><Settings className="h-4 w-4" />Settings</Link>
            <Link href="/coach" className="flex min-h-10 items-center gap-1.5 rounded-lg px-2 outline-none hover:text-slate-100 focus-visible:ring-2 focus-visible:ring-zenSage"><HelpCircle className="h-4 w-4" />Get help</Link>
          </div>
        </div>
      </aside>

      <div className="min-w-0 lg:pl-72">
        <header className="sticky top-0 z-30 flex min-h-[4.5rem] items-center justify-between gap-4 border-b border-slate-800/80 bg-slate-950/80 px-4 py-3 backdrop-blur-xl sm:px-6 lg:px-8">
          <div className="flex min-w-0 items-center gap-3">
            <button type="button" aria-expanded={menuOpen} aria-controls="app-navigation" aria-label="Open navigation" onClick={() => setMenuOpen(true)} className="icon-button lg:hidden">
              <Menu className="h-5 w-5" />
            </button>
            <div className="min-w-0">
              <p className="truncate text-lg font-black tracking-tight text-slate-100 sm:text-xl">{title}</p>
              <p className="hidden truncate text-xs text-slate-400 sm:block">Welcome back, <span className="font-semibold text-slate-200">{firstName}</span>. Your latest data shapes today&apos;s guidance.</p>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-2">
            <Link href="/coach" className="hidden min-h-10 items-center gap-2 rounded-xl border border-emerald-400/25 bg-emerald-400/10 px-3 text-xs font-bold text-emerald-300 outline-none transition-colors hover:bg-emerald-400/15 focus-visible:ring-2 focus-visible:ring-zenSage sm:flex">
              <Sparkles className="h-4 w-4" />
              Ask Zen coach
            </Link>
            <div className="relative">
              <button type="button" aria-expanded={profileOpen} aria-label="Open account menu" onClick={() => setProfileOpen((open) => !open)} className="flex min-h-11 items-center gap-2 rounded-xl border border-slate-800 bg-slate-900 px-2.5 text-left outline-none transition-colors hover:border-slate-700 focus-visible:ring-2 focus-visible:ring-zenSage">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-400/10 text-emerald-300"><UserRound className="h-4 w-4" /></span>
                <span className="hidden max-w-32 truncate text-xs font-bold text-slate-200 md:block">{user?.full_name || "Athlete"}</span>
                <ChevronDown className="hidden h-3.5 w-3.5 text-slate-400 md:block" />
              </button>
              {profileOpen ? (
                <div className="absolute right-0 mt-2 w-64 rounded-2xl border border-slate-800 bg-slate-900 p-2 shadow-2xl">
                  <div className="border-b border-slate-800 px-3 py-2">
                    <p className="truncate text-sm font-semibold text-slate-100">{user?.full_name || "Athlete"}</p>
                    <p className="truncate text-xs text-slate-400">{user?.email}</p>
                  </div>
                  <Link href="/settings" onClick={() => setProfileOpen(false)} className="mt-1 flex min-h-10 items-center gap-2 rounded-xl px-3 text-sm text-slate-300 hover:bg-slate-800"><Settings className="h-4 w-4" />Account settings</Link>
                  <button type="button" onClick={onLogout} className="flex min-h-10 w-full items-center gap-2 rounded-xl px-3 text-sm text-slate-300 hover:bg-slate-800"><LogOut className="h-4 w-4" />Log out</button>
                </div>
              ) : null}
            </div>
          </div>
        </header>

        <main id="main-content" className="min-w-0 p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
