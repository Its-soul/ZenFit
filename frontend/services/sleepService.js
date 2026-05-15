import apiClient from "./apiClient";

export async function getSleepLogs() {
  const response = await apiClient.get("/sleep/logs");
  return response.data;
}

export async function createSleepLog(payload) {
  const response = await apiClient.post("/sleep/logs", payload);
  return response.data;
}

