import apiClient from "./apiClient";

export async function getWorkoutSessions() {
  const response = await apiClient.get("/workouts/sessions");
  return response.data;
}

export async function getTodayWorkout() {
  const response = await apiClient.get("/workouts/today");
  return response.data;
}

export async function createWorkoutSession(payload) {
  const response = await apiClient.post("/workouts/sessions", payload);
  return response.data;
}

export async function completeWorkoutSession(sessionId) {
  const response = await apiClient.post(`/workouts/sessions/${sessionId}/complete`);
  return response.data;
}

export async function missWorkoutSession(sessionId) {
  const response = await apiClient.post(`/workouts/sessions/${sessionId}/miss`);
  return response.data;
}

export async function rescheduleWorkoutSession(sessionId, payload) {
  const response = await apiClient.post(`/workouts/sessions/${sessionId}/reschedule`, payload);
  return response.data;
}
