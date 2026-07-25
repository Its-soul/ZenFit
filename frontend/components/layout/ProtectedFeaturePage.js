"use client";

import { AppShell } from "@/components/layout/AppShell";
import { useAuth } from "@/hooks/useAuth";

export function ProtectedFeaturePage({ title, description, children }) {
  const { user, loading, logout } = useAuth({ requireAuth: true });

  if (loading) {
    return <main className="flex min-h-screen items-center justify-center text-muted">Loading...</main>;
  }

  if (!user) {
    return <main className="flex min-h-screen items-center justify-center text-muted">Redirecting...</main>;
  }

  return (
    <AppShell user={user} onLogout={logout}>
      <div className="mx-auto max-w-[96rem] animate-page-in">
        <header className="mb-6">
          <p className="eyebrow">Your plan, backed by your data</p>
          <h1 className="mt-2 break-words text-[clamp(1.8rem,5vw,2.5rem)] font-black tracking-[-0.035em]">{title}</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-muted sm:text-base">{description}</p>
        </header>
        <div>{children}</div>
      </div>
    </AppShell>
  );
}
