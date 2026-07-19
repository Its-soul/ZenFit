"use client";

import { Activity, Bot, CalendarDays, HeartPulse, LogOut, Menu, Moon, Salad, Settings, Sparkles, X } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/Button";

const navItems = [
  { href: "/dashboard", label: "Today", icon: Sparkles },
  { href: "/workouts", label: "Workouts", icon: Activity },
  { href: "/nutrition", label: "Nutrition", icon: Salad },
  { href: "/recovery", label: "Recovery", icon: HeartPulse },
  { href: "/sleep", label: "Sleep", icon: Moon },
  { href: "/coach", label: "Coach", icon: Bot },
  { href: "/analytics", label: "Progress", icon: CalendarDays },
  { href: "/settings", label: "Settings", icon: Settings }
];

export function AppShell({ children, user, onLogout }) {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="min-h-screen overflow-x-clip px-3 py-3 sm:px-4 md:px-6 md:py-5">
      <header className="panel sticky top-3 z-40 mx-auto mb-4 max-w-[var(--content-max)] rounded-[var(--radius-md)] p-3 md:hidden">
        <div className="flex items-center justify-between gap-4">
          <Link href="/dashboard" className="flex min-w-0 items-center gap-3" onClick={() => setMenuOpen(false)}>
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-zenCream text-slate-950"><Sparkles className="h-5 w-5" /></span>
            <span className="min-w-0"><span className="block font-semibold">ZenFit</span><span className="block truncate text-sm text-muted">Your plan for today</span></span>
          </Link>
          <button type="button" aria-expanded={menuOpen} aria-controls="mobile-navigation" aria-label={menuOpen ? "Close navigation" : "Open navigation"} onClick={() => setMenuOpen((open) => !open)} className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-white/10 outline-none transition-colors hover:bg-white/10 focus-visible:ring-2 focus-visible:ring-zenSage">
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
        {menuOpen ? <nav id="mobile-navigation" aria-label="Main navigation" className="mt-3 grid grid-cols-2 gap-2 border-t border-white/10 pt-3">
          {navItems.map((item) => { const Icon = item.icon; const active = pathname === item.href; return <Link key={item.href} href={item.href} onClick={() => setMenuOpen(false)} aria-current={active ? "page" : undefined} className={`flex min-h-12 items-center gap-2 rounded-xl px-3 text-sm font-medium outline-none transition-colors focus-visible:ring-2 focus-visible:ring-zenSage ${active ? "bg-zenCream text-[#151a15]" : "bg-white/[0.04] text-slate-200 hover:bg-white/10"}`}><Icon className="h-4 w-4 shrink-0" />{item.label}</Link>; })}
          <button type="button" onClick={onLogout} className="col-span-2 flex min-h-12 items-center gap-2 rounded-xl px-3 text-sm font-medium text-slate-300 outline-none hover:bg-white/10 focus-visible:ring-2 focus-visible:ring-zenSage"><LogOut className="h-4 w-4" />Log out</button>
        </nav> : null}
      </header>

      <div className="mx-auto flex max-w-[var(--content-max)] gap-5">
        <aside className="panel sticky top-5 hidden h-[calc(100vh-2.5rem)] w-64 shrink-0 rounded-[var(--radius-lg)] p-4 md:block">
          <div className="flex items-center gap-3 px-2 py-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-zenCream text-slate-950">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="font-semibold">ZenFit</p>
              <p className="text-xs text-muted">Daily fitness coach</p>
            </div>
          </div>

          <nav className="mt-8 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  className={`flex min-h-11 items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium outline-none transition-colors focus-visible:ring-2 focus-visible:ring-zenSage ${
                    active ? "bg-white text-slate-950" : "text-slate-300 hover:bg-white/10 hover:text-white"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="absolute bottom-4 left-4 right-4">
            <div className="soft-panel rounded-xl p-3">
              <p className="text-sm font-medium">{user?.full_name || "Athlete"}</p>
              <p className="truncate text-xs text-muted">{user?.email}</p>
              <Button variant="ghost" className="mt-3 w-full justify-start px-2" onClick={onLogout}>
                <LogOut className="h-4 w-4" />
                Logout
              </Button>
            </div>
          </div>
        </aside>

        <main className="min-w-0 flex-1" id="main-content">{children}</main>
      </div>
    </div>
  );
}
