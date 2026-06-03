import apiClient from "./apiClient";
import { clearAuthSession, getAccessToken, saveAuthSession } from "@/lib/authStorage";

export async function register(payload) {
  const response = await apiClient.post("/auth/register", payload);
  saveAuthSession(response.data.access_token, response.data.refresh_token, response.data.user);
  return response.data;
}

export async function login(payload) {
  const response = await apiClient.post("/auth/login", payload);
  saveAuthSession(response.data.access_token, response.data.refresh_token, response.data.user);
  return response.data;
}

export async function getMe() {
  const response = await apiClient.get("/auth/me");
  return response.data;
}

export async function logout() {
  if (getAccessToken()) {
    try {
      await apiClient.post("/auth/logout");
    } catch {
      // Clearing the local session is still correct if the server is unreachable.
    }
  }
  clearAuthSession();
}

export async function requestPasswordReset(email) {
  const response = await apiClient.post("/auth/password-reset/request", { email });
  return response.data;
}

export async function confirmPasswordReset(resetToken, newPassword) {
  const response = await apiClient.post("/auth/password-reset/confirm", {
    reset_token: resetToken,
    new_password: newPassword
  });
  return response.data;
}
