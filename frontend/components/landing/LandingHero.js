import { ArrowRight, Play, ShieldCheck, Sparkles } from "lucide-react";
import Link from "next/link";

import HeroDashboardPreview from "./HeroDashboardPreview";

export default function LandingHero() {
  return (
    <section className="relative isolate overflow-hidden border-b border-slate-800/80 bg-[#070b12]">
      <div aria-hidden="true" className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_18%_20%,rgba(16,185,129,0.18),transparent_30%),radial-gradient(circle_at_82%_16%,rgba(20,184,166,0.12),transparent_25%),linear-gradient(180deg,#070b12,#0b1220)]" />
      <nav aria-label="Public navigation" className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-5 sm:px-8">
        <Link href="/" className="flex items-center gap-3 rounded-xl outline-none focus-visible:ring-2 focus-visible:ring-zenSage">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-300 to-teal-500 text-lg font-black text-slate-950 shadow-[0_10px_28px_rgba(52,211,153,0.22)]">Z</span>
          <span><span className="block font-bold tracking-tight text-slate-100">ZenFit</span><span className="block text-xs text-slate-400">Adaptive daily fitness</span></span>
        </Link>
        <div className="flex items-center gap-2">
          <Link href="/auth/login" className="inline-flex min-h-11 items-center rounded-xl px-4 text-sm font-semibold text-slate-200 outline-none hover:bg-slate-800/70 focus-visible:ring-2 focus-visible:ring-zenSage">Sign in</Link>
          <Link href="/auth/register" className="hidden min-h-11 items-center rounded-xl bg-emerald-300 px-4 text-sm font-bold text-slate-950 outline-none hover:bg-emerald-200 focus-visible:ring-2 focus-visible:ring-emerald-100 sm:inline-flex">Get started</Link>
        </div>
      </nav>

      <div className="mx-auto grid min-h-[calc(92vh-5rem)] max-w-7xl items-center gap-12 px-5 py-14 sm:px-8 lg:grid-cols-[minmax(0,1.05fr)_minmax(22rem,0.95fr)] lg:py-20">
        <div className="min-w-0 animate-page-in">
          <p className="inline-flex items-center gap-2 rounded-full border border-emerald-400/25 bg-emerald-400/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.08em] text-emerald-300">
            <Sparkles className="h-4 w-4" />
            Guidance that adapts daily
          </p>
          <h1 className="mt-6 max-w-[13ch] text-[clamp(2.8rem,7vw,5.5rem)] font-black leading-[1.02] tracking-[-0.055em] text-slate-100">
            Fitness that adapts to your <span className="bg-gradient-to-r from-emerald-300 via-teal-300 to-cyan-300 bg-clip-text text-transparent">real life.</span>
          </h1>
          <p className="mt-6 max-w-2xl text-[clamp(1rem,1.7vw,1.15rem)] leading-8 text-slate-300">ZenFit brings workouts, recovery, nutrition, sleep, and supportive coaching into one clear plan shaped by what you actually log.</p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link href="/auth/register" className="inline-flex min-h-[3.25rem] items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-300 via-teal-300 to-emerald-400 px-7 py-3.5 font-bold text-slate-950 shadow-[0_16px_38px_rgba(52,211,153,0.2)] outline-none transition-transform hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-emerald-100">
              Build my plan <ArrowRight className="h-4 w-4" />
            </Link>
            <Link href="/auth/login" className="inline-flex min-h-[3.25rem] items-center justify-center gap-2 rounded-2xl border border-slate-700 bg-slate-900/70 px-7 py-3.5 font-semibold text-slate-100 outline-none hover:bg-slate-800 focus-visible:ring-2 focus-visible:ring-zenSage">
              <Play className="h-4 w-4 fill-current" /> Continue my plan
            </Link>
          </div>
          <p className="mt-6 flex items-start gap-2 text-sm leading-6 text-slate-400"><ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-emerald-300" />Your account and health data stay behind authenticated backend APIs.</p>
        </div>

        <div className="relative mx-auto w-full max-w-[38rem] lg:max-w-none">
          <div aria-hidden="true" className="absolute -inset-6 rounded-[3rem] bg-emerald-400/10 blur-3xl" />
          <HeroDashboardPreview />
        </div>
      </div>
    </section>
  );
}
