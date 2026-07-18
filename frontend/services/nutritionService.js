import apiClient from "./apiClient";

export async function getTodayNutrition() {
  const response = await apiClient.get("/nutrition/today");
  return response.data;
}

export async function createMeal(payload) {
  const response = await apiClient.post("/nutrition/meals", payload);
  return response.data;
}

export async function lookupMeal(query) {
  const response = await apiClient.post("/nutrition/meals/lookup", { query });
  return response.data;
}

export async function analyzeMealImage(file, onProgress) {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiClient.post("/nutrition/meals/analyze-image", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (event) => {
      if (onProgress && event.total) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    }
  });
  return response.data;
}

export async function analyzeMealImageLocal(file, onProgress) {
  const formData = new FormData(); formData.append("file", file);
  const response = await apiClient.post("/nutrition/meals/analyze-image-local", formData, {
    headers: { "Content-Type": "multipart/form-data" }, timeout: 120000,
    onUploadProgress: (event) => { if (onProgress && event.total) onProgress(Math.round((event.loaded/event.total)*100)); }
  });
  return response.data;
}

export async function confirmMealAnalysis(payload) {
  const response = await apiClient.post("/nutrition/meals/confirm-analysis", payload);
  return response.data;
}
