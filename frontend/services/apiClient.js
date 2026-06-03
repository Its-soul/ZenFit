import axios from "axios";

import { clearAuthSession, getAccessToken, getRefreshToken, saveAuthSession } from "@/lib/authStorage";

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  timeout: 15000
});

const refreshClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  timeout: 15000
});

let refreshRequest = null;

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function refreshAuthSession() {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    clearAuthSession();
    throw new Error("Missing refresh token");
  }

  if (!refreshRequest) {
    refreshRequest = refreshClient
      .post("/auth/refresh", { refresh_token: refreshToken })
      .then((response) => {
        saveAuthSession(response.data.access_token, response.data.refresh_token, response.data.user);
        return response.data.access_token;
      })
      .catch((error) => {
        clearAuthSession();
        throw error;
      })
      .finally(() => {
        refreshRequest = null;
      });
  }

  return refreshRequest;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const requestUrl = originalRequest?.url || "";
    const isAuthEndpoint = requestUrl.startsWith("/auth/login")
      || requestUrl.startsWith("/auth/register")
      || requestUrl.startsWith("/auth/refresh")
      || requestUrl.startsWith("/auth/password-reset");
    if (error.response?.status !== 401 || !originalRequest || originalRequest._authRetry || isAuthEndpoint) {
      return Promise.reject(error);
    }

    originalRequest._authRetry = true;
    try {
      const token = await refreshAuthSession();
      originalRequest.headers = originalRequest.headers || {};
      originalRequest.headers.Authorization = `Bearer ${token}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      return Promise.reject(refreshError);
    }
  }
);

export function getApiErrorMessage(error, fallback = "Something went wrong") {
  const detail = error.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).filter(Boolean).join(" ") || fallback;
  }
  return detail || error.message || fallback;
}

export default apiClient;
