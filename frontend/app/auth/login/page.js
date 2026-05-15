"use client";

import { Activity, ArrowRight } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { login } from "@/services/authService";

export default function LoginPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const session = await login(form);
      router.replace(session.user.onboarding_complete ? "/dashboard" : "/onboarding");
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Unable to log in");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="glass w-full max-w-md rounded-2xl p-8">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyanGlow text-slate-950">
            <Activity className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Welcome back</h1>
            <p className="text-sm text-muted">Sign in to your adaptive fitness OS.</p>
          </div>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <label className="block">
            <span className="mb-2 block text-sm text-slate-200">Email</span>
            <Input type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm text-slate-200">Password</span>
            <Input type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} required />
          </label>

          {error ? <p className="rounded-lg border border-red-400/30 bg-red-500/10 px-3 py-2 text-sm text-red-100">{error}</p> : null}

          <Button className="w-full" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
            <ArrowRight className="h-4 w-4" />
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-muted">
          New here?{" "}
          <Link className="font-medium text-cyanGlow" href="/auth/register">
            Create account
          </Link>
        </p>
      </div>
    </main>
  );
}

