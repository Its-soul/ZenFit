import apiClient from "./apiClient";

export async function searchMemory(query, limit = 8) {
  const response = await apiClient.post("/memory/search", { query, limit });
  return response.data.results;
}

