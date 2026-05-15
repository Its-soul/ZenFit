"use client";

import { useWebSocket } from "./useWebSocket";

export function useRealtimeDashboard() {
  return useWebSocket("dashboard");
}

