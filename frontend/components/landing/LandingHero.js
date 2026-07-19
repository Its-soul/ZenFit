import { ArrowRight, Sparkles } from "lucide-react";
import Link from "next/link";
import HeroDashboardPreview from "./HeroDashboardPreview";

function StatusCard({ dark = false, title, body, className = "" }) {
  return (
    <div className={`rounded-2xl px-4 py-3 shadow-xl sm:rounded-3xl sm:px-5 sm:py-4 ${dark ? "bg-[#121711] text-white" : "bg-white/80 text-[#121711]"} ${className}`}>
      <p className="whitespace-nowrap text-sm font-semibold">{title}</p>
      <p className={`mt-0.5 whitespace-nowrap text-xs ${dark ? "text-slate-300" : "text-slate-600"}`}>{body}</p>
    </div>
  );
}

export default function LandingHero() {
  return (
    <section className="landing-hero relative isolate overflow-hidden">
      <div aria-hidden="true" className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_18%_18%,rgba(143,232,197,0.55),transparent_28%),radial-gradient(circle_at_82%_20%,rgba(246,199,121,0.35),transparent_26%),linear-gradient(180deg,#f7f2e8,#ece5d7)]" />
      <div className="relative mx-auto grid min-h-[min(92vh,900px)] max-w-7xl items-center gap-x-[clamp(3rem,6vw,6.5rem)] gap-y-12 px-[clamp(1.25rem,4vw,3rem)] py-[clamp(2rem,6vw,5rem)] xl:grid-cols-[minmax(0,1fr)_minmax(22rem,27.5rem)]">
        <div className="min-w-0">
          <Link href="/" className="mb-[clamp(1.75rem,4vw,2.5rem)] inline-flex items-center gap-2 rounded-full bg-white/70 px-4 py-2 text-sm font-semibold shadow-sm">
            <Sparkles className="h-4 w-4" /> ZenFit
          </Link>
          <h1 className="max-w-[12.5ch] text-[clamp(2.75rem,6.1vw,5.75rem)] font-semibold leading-[1.02] tracking-[-0.04em]">Fitness guidance that adapts to your real life.</h1>
          <p className="mt-6 max-w-[42rem] text-[clamp(1rem,1.6vw,1.125rem)] leading-[1.75] text-slate-700">ZenFit helps you stay consistent with personalized workouts, recovery insights, nutrition tracking, and an AI coach that understands your habits.</p>
          <div className="mt-8 flex flex-wrap gap-3 sm:mt-9">
            <Link href="/auth/register" className="inline-flex min-h-12 flex-1 items-center justify-center gap-2 rounded-full bg-[#121711] px-6 py-3 text-sm font-semibold text-white transition-transform hover:-translate-y-0.5 hover:bg-[#20281f] sm:flex-none">Start Free <ArrowRight className="h-4 w-4" /></Link>
            <Link href="/auth/login" className="inline-flex min-h-12 flex-1 items-center justify-center rounded-full border border-[#121711]/15 bg-white/60 px-6 py-3 text-sm font-semibold transition-transform hover:-translate-y-0.5 hover:bg-white sm:flex-none">See Demo</Link>
          </div>
        </div>
        <div className="mx-auto w-full max-w-[40rem] xl:max-w-[27.5rem]">
          <div className="mb-4 flex flex-wrap items-end justify-between gap-3 px-1 sm:mb-5 sm:flex-nowrap xl:-mx-8 xl:px-0">
            <StatusCard dark title="Recovery Insight" body="Go lighter today" className="hero-status-card--recovery" />
            <StatusCard title="4 day streak" body="Small progress still counts" className="hero-status-card--streak" />
          </div>
          <HeroDashboardPreview />
        </div>
      </div>
    </section>
  );
}
