"use client";

import { AppShell } from "@/components/layout/AppShell";
import { SurfacePanel } from "@/components/common/SurfacePanel";
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
      <SurfacePanel className="min-w-0 p-[clamp(1rem,3vw,1.5rem)]">
        <h1 className="break-words text-[clamp(1.75rem,5vw,2rem)] font-semibold">{title}</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">{description}</p>
        <div className="mt-6">{children}</div>
      </SurfacePanel>
    </AppShell>
  );
}
