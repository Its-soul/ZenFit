import { Bot, Dumbbell, UtensilsCrossed, Waves } from "lucide-react";
import Link from "next/link";

import LandingBackgroundVideo from "./LandingBackgroundVideo";

const featureCards = [
  {
    title: "Personalized Workouts",
    body: "Adaptive plans that evolve with your progress. Never plateau, always improve.",
    icon: Dumbbell
  },
  {
    title: "AI Coach",
    body: "Real-time guidance and habit analysis. Your coach is available 24/7.",
    icon: Bot
  },
  {
    title: "Nutrition Tracking",
    body: "Seamless macro and calorie tracking. Fuel your body for optimal recovery.",
    icon: UtensilsCrossed
  }
];

export default function LandingHero() {
  return (
    <section className="relative isolate min-h-[92vh] overflow-hidden bg-[#eef5f4] text-slate-950">
      <div aria-hidden="true" className="absolute inset-0 -z-30 bg-[linear-gradient(135deg,#f8fbff_0%,#e6f8ef_42%,#d7f2fb_100%)]" />
      <LandingBackgroundVideo />
      <div aria-hidden="true" className="absolute inset-0 -z-10 bg-[linear-gradient(180deg,rgba(255,255,255,0.22)_0%,rgba(255,255,255,0.58)_42%,rgba(247,250,252,0.76)_100%)]" />

      <nav aria-label="Public navigation" className="mx-auto flex w-[min(75rem,calc(100%-2rem))] items-center justify-between gap-4 rounded-2xl border border-white/65 bg-white/42 px-4 py-3 shadow-[0_20px_70px_rgba(15,23,42,0.13)] backdrop-blur-md sm:mt-5 sm:px-6">
        <Link href="/" className="flex items-center gap-2 rounded-xl text-slate-950 outline-none focus-visible:ring-2 focus-visible:ring-emerald-500">
          <Waves className="h-8 w-8 text-teal-400" aria-hidden="true" />
          <span className="text-2xl font-black tracking-normal">ZenFit</span>
        </Link>
        <div className="hidden items-center gap-8 text-sm font-medium text-slate-950 md:flex">
          <Link href="#features" className="rounded-lg outline-none hover:text-teal-700 focus-visible:ring-2 focus-visible:ring-emerald-500">Features</Link>
          <Link href="#how-it-works" className="rounded-lg outline-none hover:text-teal-700 focus-visible:ring-2 focus-visible:ring-emerald-500">How it works</Link>
          <Link href="#pricing" className="rounded-lg outline-none hover:text-teal-700 focus-visible:ring-2 focus-visible:ring-emerald-500">Pricing</Link>
          <Link href="#about" className="rounded-lg outline-none hover:text-teal-700 focus-visible:ring-2 focus-visible:ring-emerald-500">About</Link>
        </div>
        <div className="flex items-center gap-2 sm:gap-3">
          <Link href="/auth/login" className="hidden min-h-10 items-center rounded-full px-4 text-sm font-medium text-slate-900 outline-none hover:bg-white/40 focus-visible:ring-2 focus-visible:ring-emerald-500 sm:inline-flex">Sign in</Link>
          <Link href="/auth/register" className="inline-flex min-h-11 items-center rounded-full bg-gradient-to-r from-emerald-400 via-teal-400 to-sky-400 px-5 text-sm font-black text-slate-950 shadow-[0_14px_38px_rgba(20,184,166,0.36)] outline-none transition-transform hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-emerald-600">Build my plan</Link>
        </div>
      </nav>

      <div className="mx-auto flex min-h-[calc(92vh-5.5rem)] w-[min(75rem,calc(100%-2rem))] flex-col items-center justify-center px-1 pb-12 pt-12 text-center sm:px-6 lg:pt-16">
        <div className="animate-page-in">
          <h1 className="mx-auto max-w-3xl text-5xl font-black leading-[1.08] tracking-normal text-black sm:text-6xl lg:text-7xl">
            Fitness guidance that adapts to your real life.
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-slate-950 sm:text-lg">
            ZenFit helps you stay consistent with personalized workouts, recovery insights, nutrition tracking, and an AI coach that understands your habits.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link href="/auth/register" className="inline-flex min-h-12 w-full items-center justify-center rounded-full bg-gradient-to-r from-emerald-400 via-teal-400 to-sky-400 px-8 text-base font-black text-slate-950 shadow-[0_20px_45px_rgba(20,184,166,0.32)] outline-none transition-transform hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-emerald-700 sm:w-auto">
              Build my plan
            </Link>
            <Link href="/auth/login" className="inline-flex min-h-12 w-full items-center justify-center rounded-full border border-white/80 bg-white/22 px-8 text-base font-semibold text-slate-950 shadow-[inset_0_1px_0_rgba(255,255,255,0.55)] outline-none backdrop-blur-md transition-colors hover:bg-white/40 focus-visible:ring-2 focus-visible:ring-emerald-700 sm:w-auto">
              Sign in
            </Link>
          </div>
        </div>

        <div id="features" className="mt-14 grid w-full max-w-4xl gap-5 text-left md:grid-cols-3">
          {featureCards.map(({ title, body, icon: Icon }) => (
            <article key={title} className="min-h-60 rounded-2xl border border-white/70 bg-white/38 p-6 shadow-[0_24px_70px_rgba(15,23,42,0.13)] backdrop-blur-md">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-400/18 text-teal-500 shadow-[0_0_26px_rgba(20,184,166,0.32)]">
                <Icon className="h-10 w-10" aria-hidden="true" />
              </div>
              <h2 className="mt-7 text-xl font-black tracking-normal text-black">{title}</h2>
              <p className="mt-3 text-base leading-6 text-slate-950">{body}</p>
            </article>
          ))}
        </div>

      </div>
    </section>
  );
}
