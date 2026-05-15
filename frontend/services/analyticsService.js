import apiClient from "./apiClient";

export async function getPredictiveAnalytics() {
  const response = await apiClient.get("/analytics/predictive");
  return response.data;
}

export async function getLatestWeeklyReport() {
  const response = await apiClient.get("/analytics/weekly-report/latest");
  return response.data;
}

export async function getAnalyticsHistory(days = 90) {
  const response = await apiClient.get(`/analytics/history?days=${days}`);
  return response.data;
}
