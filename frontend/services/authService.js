import apiClient from "./apiClient";
import { clearAuthSession, saveAuthSession } from "@/lib/authStorage";

export async function register(payload) {
  const response = await apiClient.post("/auth/register", payload);
  saveAuthSession(response.data.access_token, response.data.user);
  return response.data;
}

export async function login(payload) {
  const response = await apiClient.post("/auth/login", payload);
  saveAuthSession(response.data.access_token, response.data.user);
  return response.data;
}

export async function getMe() {
  const response = await apiClient.get("/auth/me");
  return response.data;
}

export function logout() {
  clearAuthSession();
}

