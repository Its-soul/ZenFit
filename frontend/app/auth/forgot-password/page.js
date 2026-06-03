"use client";

import { ArrowLeft, Mail } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { getApiErrorMessage } from "@/services/apiClient";
import { requestPasswordReset } from "@/services/authService";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [notice, setNotice] = useState("");
  const [resetToken, setResetToken] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    setResetToken("");
    setLoading(true);
    try {
      const response = await requestPasswordReset(email);
      setNotice(response.message || "If that email exists, a password reset has been prepared.");
      if (response.reset_token) setResetToken(response.reset_token);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Unable to prepare a password reset."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="panel w-full max-w-md rounded-2xl p-8">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-zenCream text-slate-950">
            <Mail className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Reset password</h1>
            <p className="text-sm text-muted">Prepare a secure reset link.</p>
          </div>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <label className="block">
            <span className="mb-2 block text-sm text-slate-200">Email</span>
            <Input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>

          {notice ? <p className="rounded-lg border border-zenSage/30 bg-zenSage/10 px-3 py-2 text-sm text-zenSage">{notice}</p> : null}
          {resetToken ? (
            <Link className="block rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-slate-100" href={`/auth/reset-password?token=${encodeURIComponent(resetToken)}`}>
              Continue to reset password
            </Link>
          ) : null}
          {error ? <p className="rounded-lg border border-red-400/30 bg-red-500/10 px-3 py-2 text-sm text-red-100">{error}</p> : null}

          <Button className="w-full" disabled={loading}>
            {loading ? "Preparing..." : "Prepare reset"}
          </Button>
        </form>

        <Link className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-zenSage" href="/auth/login">
          <ArrowLeft className="h-4 w-4" />
          Back to sign in
        </Link>
      </div>
    </main>
  );
}
