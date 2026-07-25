import { Activity, ArrowRight, CheckCircle2, HeartPulse, Moon, Salad, Sparkles } from "lucide-react";
import Link from "next/link";

import LandingHero from "../components/landing/LandingHero";

const features = [
  { title: "Training that can change", body: "Plan, complete, move, or lighten sessions without losing the thread of your week.", icon: Activity, tone: "text-emerald-300 bg-emerald-400/10 border-emerald-400/20" },
  { title: "Recovery with context", body: "Sleep and body check-ins turn into practical guidance instead of another score to chase.", icon: HeartPulse, tone: "text-cyan-300 bg-cyan-400/10 border-cyan-400/20" },
  { title: "Nutrition you can actually log", body: "Use food lookup, manual entry, or local meal analysis, then review before saving.", icon: Salad, tone: "text-amber-300 bg-amber-400/10 border-amber-400/20" }
];

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-x-clip bg-[#070b12] text-slate-100">
      <LandingHero />

      <section className="mx-auto max-w-7xl px-5 py-20 sm:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <p className="eyebrow">One connected fitness rhythm</p>
          <h2 className="mt-3 text-3xl font-black tracking-[-0.035em] sm:text-4xl">Clear enough for busy days. Flexible enough for real ones.</h2>
          <p className="mt-4 leading-7 text-slate-400">Every surface connects to the same account-backed plan, so logging an action helps the next recommendation make more sense.</p>
        </div>
        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {features.map(({ title, body, icon: Icon, tone }) => (
            <article key={title} className="panel group rounded-3xl p-6 transition-[border-color,transform] hover:-translate-y-1 hover:border-emerald-400/25">
              <span className={`flex h-12 w-12 items-center justify-center rounded-2xl border ${tone}`}><Icon className="h-6 w-6" /></span>
              <h3 className="mt-5 text-xl font-bold">{title}</h3>
              <p className="mt-3 text-sm leading-7 text-slate-400">{body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="border-y border-slate-800/80 bg-slate-900/45 px-5 py-20 sm:px-8">
        <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[0.85fr_1.15fr] lg:items-center">
          <div>
            <p className="eyebrow">How the day stays connected</p>
            <h2 className="mt-3 text-3xl font-black tracking-[-0.035em] sm:text-4xl">Log what matters. Get one useful next move.</h2>
            <p className="mt-4 leading-7 text-slate-400">ZenFit uses the data you provide through its real workout, nutrition, sleep, and recovery tools. When a smart feature is unavailable, the manual path remains usable.</p>
            <Link href="/auth/register" className="mt-7 inline-flex min-h-12 items-center gap-2 rounded-xl bg-emerald-300 px-5 font-bold text-slate-950 outline-none hover:bg-emerald-200 focus-visible:ring-2 focus-visible:ring-emerald-100">Create my plan <ArrowRight className="h-4 w-4" /></Link>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {[
              ["1", "Check in", "Share sleep, fatigue, soreness, or stress.", Moon],
              ["2", "See the adjustment", "Review the session and recovery guidance.", Sparkles],
              ["3", "Take action", "Complete, move, or lighten the workout.", Activity],
              ["4", "Build the pattern", "Progress views reflect your logged activity.", CheckCircle2]
            ].map(([number, title, body, Icon]) => (
              <div key={number} className="panel rounded-2xl p-5">
                <div className="flex items-center justify-between"><span className="text-xs font-black text-emerald-300">STEP {number}</span><Icon className="h-5 w-5 text-slate-500" /></div>
                <h3 className="mt-4 font-bold">{title}</h3><p className="mt-2 text-sm leading-6 text-slate-400">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-10 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-8">
        <p>ZenFit · Adaptive daily fitness guidance</p>
        <div className="flex gap-4"><Link href="/auth/login" className="hover:text-slate-200">Sign in</Link><Link href="/auth/register" className="hover:text-slate-200">Create account</Link></div>
      </footer>
    </main>
  );
}
