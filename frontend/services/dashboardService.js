import apiClient from "./apiClient";

export async function getTodayDashboard() {
  const response = await apiClient.get("/dashboard/today");
  return response.data;
}

