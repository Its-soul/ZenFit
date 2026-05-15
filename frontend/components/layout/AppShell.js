"use client";

import { Activity, BarChart3, Bot, Brain, LogOut, Moon, Salad, Settings, Sparkles } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { Button } from "@/components/ui/Button";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: Sparkles },
  { href: "/workouts", label: "Workouts", icon: Activity },
  { href: "/nutrition", label: "Nutrition", icon: Salad },
  { href: "/recovery", label: "Recovery", icon: Brain },
  { href: "/sleep", label: "Sleep", icon: Moon },
  { href: "/coach", label: "AI Coach", icon: Bot },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings }
];

export function AppShell({ children, user, onLogout }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen px-4 py-4 md:px-6">
      <div className="mx-auto flex max-w-7xl gap-5">
        <aside className="panel sticky top-4 hidden h-[calc(100vh-2rem)] w-64 shrink-0 rounded-xl p-4 md:block">
          <div className="flex items-center gap-3 px-2 py-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-white text-slate-950">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="font-semibold">AI Fitness OS</p>
              <p className="text-xs text-muted">Adaptive command center</p>
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
                  className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${
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

        <main className="min-w-0 flex-1">{children}</main>
      </div>
    </div>
  );
}
