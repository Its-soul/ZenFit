"use client";

import { ArrowLeft, KeyRound } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { getApiErrorMessage } from "@/services/apiClient";
import { confirmPasswordReset } from "@/services/authService";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [resetToken, setResetToken] = useState(() => {
    if (typeof window === "undefined") return "";
    return new URLSearchParams(window.location.search).get("token") || "";
  });
  const [newPassword, setNewPassword] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setNotice("");
    setLoading(true);
    try {
      await confirmPasswordReset(resetToken, newPassword);
      setNotice("Password reset complete. Redirecting to sign in...");
      setTimeout(() => router.replace("/auth/login"), 900);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Unable to reset password. Request a new reset link."));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="panel w-full max-w-md rounded-2xl p-8">
        <div className="mb-8 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-zenCream text-slate-950">
            <KeyRound className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Choose new password</h1>
            <p className="text-sm text-muted">Use a fresh password for this account.</p>
          </div>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <label className="block">
            <span className="mb-2 block text-sm text-slate-200">Reset token</span>
            <Input value={resetToken} onChange={(event) => setResetToken(event.target.value)} required />
          </label>

          <label className="block">
            <span className="mb-2 block text-sm text-slate-200">New password</span>
            <Input type="password" minLength={8} value={newPassword} onChange={(event) => setNewPassword(event.target.value)} required />
          </label>

          {notice ? <p className="rounded-lg border border-zenSage/30 bg-zenSage/10 px-3 py-2 text-sm text-zenSage">{notice}</p> : null}
          {error ? <p className="rounded-lg border border-red-400/30 bg-red-500/10 px-3 py-2 text-sm text-red-100">{error}</p> : null}

          <Button className="w-full" disabled={loading}>
            {loading ? "Resetting..." : "Reset password"}
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
