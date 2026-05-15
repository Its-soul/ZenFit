import apiClient from "./apiClient";

export async function sendRecommendationFeedback(recommendationId, feedbackType, notes = "") {
  const response = await apiClient.post(`/recommendations/${recommendationId}/feedback`, {
    feedback_type: feedbackType,
    notes
  });
  return response.data;
}
