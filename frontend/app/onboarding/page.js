"use client";

import OnboardingForm from "@/components/onboarding/OnboardingForm";
import { useAuth } from "@/hooks/useAuth";

export default function OnboardingPage() {
  const { user, loading } = useAuth({ requireAuth: true });
  if (loading) return <main className="flex min-h-screen items-center justify-center px-4 text-muted">Preparing ZenFit...</main>;
  if (!user) return <main className="flex min-h-screen items-center justify-center px-4 text-muted">Redirecting...</main>;
  return <main className="flex min-h-screen min-w-0 items-center justify-center overflow-x-clip px-[clamp(1rem,4vw,2rem)] py-[clamp(1.5rem,5vw,3rem)]"><OnboardingForm /></main>;
}
