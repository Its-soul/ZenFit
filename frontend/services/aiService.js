import apiClient from "./apiClient";

export async function getAiHealth() { return (await apiClient.get("/ai/health")).data; }
export async function analyzePose(payload) { return (await apiClient.post("/ai/pose/analyze", payload)).data; }
