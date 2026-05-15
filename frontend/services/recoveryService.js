import apiClient from "./apiClient";

export async function getReadiness() {
  const response = await apiClient.get("/recovery/readiness");
  return response.data;
}

export async function createRecoveryCheckin(payload) {
  const response = await apiClient.post("/recovery/check-ins", payload);
  return response.data;
}

