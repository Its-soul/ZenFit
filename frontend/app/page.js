import { Activity, CheckCircle2, HeartPulse, Quote, Sparkles, Star } from "lucide-react";
import LandingHero from "../components/landing/LandingHero";

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

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-x-clip bg-[#f7f2e8] text-[#121711]">
      <LandingHero />

      <section className="mx-auto max-w-7xl px-6 py-20">
        <div className="grid gap-5 md:grid-cols-3">
          {features.map(([title, body, Icon]) => (
            <div key={title} className="rounded-3xl bg-white p-6 shadow-sm">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#e7f6ed]"><Icon className="h-5 w-5" /></div>
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
                <p key={item} className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-green-700" />{item}</p>
              ))}
            </div>
          </div>
          <div className="rounded-[1.5rem] bg-[#f5f1e8] p-5">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl bg-white p-5"><p className="text-sm text-slate-600">Workout completion</p><p className="mt-2 text-3xl font-semibold">86%</p></div>
              <div className="rounded-2xl bg-white p-5"><p className="text-sm text-slate-600">Recovery</p><p className="mt-2 text-3xl font-semibold">Balanced</p></div>
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
