"use client";

import { useEffect, useState } from "react";

import { getAccessToken } from "@/lib/authStorage";

export function useWebSocket(channel) {
  const [status, setStatus] = useState("idle");
  const [lastMessage, setLastMessage] = useState(null);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;

    const baseUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";
    const socket = new WebSocket(`${baseUrl}/${channel}?token=${encodeURIComponent(token)}`);

    socket.onopen = () => setStatus("connected");
    socket.onclose = () => setStatus("closed");
    socket.onerror = () => setStatus("error");
    socket.onmessage = (event) => {
      try {
        setLastMessage(JSON.parse(event.data));
      } catch {
        setLastMessage({ type: "raw", payload: event.data });
      }
    };

    return () => {
      socket.close();
    };
  }, [channel]);

  return { status, lastMessage };
}

