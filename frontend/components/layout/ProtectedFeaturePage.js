"use client";

import { AppShell } from "@/components/layout/AppShell";
import { GlassPanel } from "@/components/common/GlassPanel";
import { useAuth } from "@/hooks/useAuth";

export function ProtectedFeaturePage({ title, description, children }) {
  const { user, loading, logout } = useAuth({ requireAuth: true });

  if (loading) {
    return <main className="flex min-h-screen items-center justify-center text-muted">Loading...</main>;
  }

  return (
    <AppShell user={user} onLogout={logout}>
      <GlassPanel className="p-6">
        <h1 className="text-3xl font-semibold">{title}</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted">{description}</p>
        <div className="mt-6">{children}</div>
      </GlassPanel>
    </AppShell>
  );
}

