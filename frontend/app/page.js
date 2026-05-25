"use client";

import { Activity, ArrowRight, CheckCircle2, HeartPulse, Quote, Salad, Sparkles, Star } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function HomePage() {
  const features = [
    ["Daily Guidance", "Know exactly what to do today.", Activity],
    ["Recovery Awareness", "Train smarter based on sleep, fatigue, and recovery.", HeartPulse],
    ["Adaptive Coaching", "Your coach learns your habits and helps you stay consistent.", Sparkles]
  ];

  const testimonials = [
    ["Maya", "ZenFit helped me stop overthinking. I just open Today and follow the next step."],
    ["Leo", "The recovery guidance feels human. It helped me train lighter without feeling guilty."],
    ["Nina", "I finally have a plan that bends around real life instead of breaking when I miss a day."]
  ];

  return (
    <main className="min-h-screen overflow-hidden bg-[#f7f2e8] text-[#121711]">
      <section className="relative">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_18%,rgba(143,232,197,0.55),transparent_28%),radial-gradient(circle_at_82%_20%,rgba(246,199,121,0.35),transparent_26%),linear-gradient(180deg,#f7f2e8,#ece5d7)]" />
        <motion.div
          animate={{ y: [0, -12, 0], rotate: [0, 2, 0] }}
          transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
          className="absolute right-[10%] top-24 hidden rounded-3xl bg-white/70 px-5 py-4 shadow-2xl md:block"
        >
          <p className="text-sm font-semibold">4 day streak</p>
          <p className="text-xs text-slate-600">Small progress still counts</p>
        </motion.div>
        <motion.div
          animate={{ y: [0, 14, 0], rotate: [0, -2, 0] }}
          transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          className="absolute left-[8%] top-72 hidden rounded-3xl bg-[#121711] px-5 py-4 text-white shadow-2xl lg:block"
        >
          <p className="text-sm font-semibold">Recovery Insight</p>
          <p className="text-xs text-slate-300">Go lighter today</p>
        </motion.div>

        <div className="relative mx-auto grid min-h-[92vh] max-w-7xl items-center gap-12 px-6 py-10 lg:grid-cols-[1fr_440px]">
          <div>
            <Link href="/" className="mb-10 inline-flex items-center gap-2 rounded-full bg-white/70 px-4 py-2 text-sm font-semibold shadow-sm">
              <Sparkles className="h-4 w-4" />
              ZenFit
            </Link>
            <h1 className="max-w-4xl text-5xl font-semibold leading-[1.02] tracking-[-0.03em] md:text-7xl">
              Fitness guidance that adapts to your real life.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-700">
              ZenFit helps you stay consistent with personalized workouts, recovery insights, nutrition tracking, and an AI coach that understands your habits.
            </p>
            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Link href="/auth/register" className="inline-flex items-center justify-center gap-2 rounded-full bg-[#121711] px-6 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:bg-[#20281f]">
                Start Free
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/auth/login" className="inline-flex items-center justify-center rounded-full border border-[#121711]/15 bg-white/60 px-6 py-3 text-sm font-semibold transition hover:-translate-y-0.5 hover:bg-white">
                See Demo
              </Link>
            </div>
          </div>

          <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} className="zen-card rounded-[2rem] p-5">
            <div className="rounded-[1.5rem] bg-[#121711] p-5 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-300">Today</p>
                  <h2 className="text-2xl font-semibold">Stay on track</h2>
                </div>
                <span className="rounded-full bg-zenSage px-3 py-1 text-xs font-semibold text-[#121711]">Ready</span>
              </div>
              <div className="mt-6 grid gap-3">
                <div className="rounded-2xl bg-white/10 p-4">
                  <p className="text-sm text-slate-300">Workout</p>
                  <p className="mt-1 text-lg font-semibold">Full Body Strength</p>
                  <p className="mt-1 text-sm text-slate-300">38 min · Moderate · 5 exercises</p>
                </div>
                <div className="grid grid-cols-3 gap-3">
                  <div className="rounded-2xl bg-white/10 p-4">
                    <p className="text-xs text-slate-300">Streak</p>
                    <p className="mt-1 text-2xl font-semibold">4</p>
                  </div>
                  <div className="rounded-2xl bg-white/10 p-4">
                    <p className="text-xs text-slate-300">Recovery</p>
                    <p className="mt-1 text-2xl font-semibold">82</p>
                  </div>
                  <div className="rounded-2xl bg-white/10 p-4">
                    <p className="text-xs text-slate-300">Protein</p>
                    <p className="mt-1 text-2xl font-semibold">96g</p>
                  </div>
                </div>
                <div className="rounded-2xl bg-[#f5f1e8] p-4 text-[#121711]">
                  <p className="text-sm font-semibold">Daily Insight</p>
                  <p className="mt-1 text-sm text-slate-700">You recover better after 8+ hours of sleep. Keep today steady, not intense.</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="grid gap-5 md:grid-cols-3">
          {features.map(([title, body, Icon]) => (
            <div key={title} className="rounded-3xl bg-white p-6 shadow-sm">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#e7f6ed]">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="mt-5 text-xl font-semibold">{title}</h3>
              <p className="mt-2 leading-7 text-slate-600">{body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-[#121711] px-6 py-20 text-white">
        <div className="mx-auto max-w-7xl">
          <div className="mb-10 flex items-end justify-between gap-6">
            <div>
              <p className="text-sm font-semibold text-zenSage">Loved by consistent people</p>
              <h2 className="mt-2 text-3xl font-semibold tracking-[-0.02em]">Built for real schedules, tired days, and small wins.</h2>
            </div>
            <Star className="hidden h-8 w-8 text-zenGold md:block" />
          </div>
          <div className="grid gap-5 md:grid-cols-3">
            {testimonials.map(([name, body]) => (
              <div key={name} className="rounded-3xl bg-white/10 p-6">
                <Quote className="h-5 w-5 text-zenGold" />
                <p className="mt-5 leading-7 text-slate-200">{body}</p>
                <p className="mt-5 font-semibold">{name}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="grid gap-8 rounded-[2rem] bg-white p-6 shadow-sm lg:grid-cols-[0.9fr_1.1fr]">
          <div className="flex flex-col justify-center p-4">
            <h2 className="text-3xl font-semibold tracking-[-0.02em]">A calm plan before the day gets noisy.</h2>
            <p className="mt-4 leading-7 text-slate-600">ZenFit turns your workout, recovery, meals, and habits into one simple answer: what to do today.</p>
            <div className="mt-6 space-y-3 text-sm">
              {["Recovery-aware training", "Warm coaching when you miss a day", "Progress that feels achievable"].map((item) => (
                <p key={item} className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-700" />
                  {item}
                </p>
              ))}
            </div>
          </div>
          <div className="rounded-[1.5rem] bg-[#f5f1e8] p-5">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl bg-white p-5">
                <p className="text-sm text-slate-600">Workout completion</p>
                <p className="mt-2 text-3xl font-semibold">86%</p>
              </div>
              <div className="rounded-2xl bg-white p-5">
                <p className="text-sm text-slate-600">Recovery</p>
                <p className="mt-2 text-3xl font-semibold">Balanced</p>
              </div>
              <div className="rounded-2xl bg-white p-5 md:col-span-2">
                <p className="text-sm font-semibold">Motivational insight</p>
                <p className="mt-2 text-slate-600">You’re most consistent when the next step is under 40 minutes. Today’s plan keeps that rhythm.</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
