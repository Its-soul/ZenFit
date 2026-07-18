import apiClient, { refreshAuthSession } from "./apiClient";
import { getAccessToken } from "@/lib/authStorage";
import { API_URL } from "@/lib/runtimeConfig";

export async function sendCoachMessage(message) {
  const response = await apiClient.post("/ai-coach/messages", { message });
  return response.data;
}

export async function streamCoachMessage(message, { onToken, onMetadata } = {}) {
  const makeRequest = () => fetch(`${API_URL}/ai-coach/messages/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getAccessToken()}`
    },
    body: JSON.stringify({ message })
  });

  let response = await makeRequest();
  if (response.status === 401) {
    await refreshAuthSession();
    response = await makeRequest();
  }

  if (!response.ok || !response.body) {
    throw new Error("Unable to stream coach response");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let eventName = "message";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() || "";

    for (const chunk of chunks) {
      const lines = chunk.split("\n");
      const eventLine = lines.find((line) => line.startsWith("event:"));
      const dataLine = lines.find((line) => line.startsWith("data:"));
      if (eventLine) eventName = eventLine.replace("event:", "").trim();
      if (!dataLine) continue;
      const data = dataLine.replace("data:", "").trim();
      if (eventName === "metadata") {
        onMetadata?.(JSON.parse(data));
      } else if (eventName === "done") {
        return;
      } else {
        onToken?.(`${data} `);
      }
      eventName = "message";
    }
  }
}
