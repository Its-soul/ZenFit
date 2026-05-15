import apiClient from "./apiClient";

export async function getProfile() {
  const response = await apiClient.get("/users/me/profile");
  return response.data;
}

export async function completeOnboarding(payload) {
  const response = await apiClient.post("/users/me/onboarding", payload);
  return response.data;
}

