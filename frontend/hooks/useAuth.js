"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getMe, logout as logoutService } from "@/services/authService";
import { clearAuthSession, getAccessToken, getStoredUser } from "@/lib/authStorage";

export function useAuth({ requireAuth = false } = {}) {
  const router = useRouter();
  const [user, setUser] = useState(getStoredUser());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function loadUser() {
      const token = getAccessToken();
      if (!token) {
        if (mounted) {
          setUser(null);
          setLoading(false);
        }
        if (requireAuth) router.replace("/auth/login");
        return;
      }

      try {
        const freshUser = await getMe();
        if (!mounted) return;
        setUser(freshUser);
      } catch (error) {
        clearAuthSession();
        if (!mounted) return;
        setUser(null);
        if (requireAuth) {
          router.replace("/auth/login");
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadUser();

    return () => {
      mounted = false;
    };
  }, [requireAuth, router]);

  async function logout() {
    await logoutService();
    setUser(null);
    router.replace("/auth/login");
  }

  return { user, setUser, loading, logout };
}
