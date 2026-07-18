"use client";

import { useEffect, useState } from "react";

import { getAccessToken } from "@/lib/authStorage";
import { WS_URL } from "@/lib/runtimeConfig";

export function useWebSocket(channel) {
  const [status, setStatus] = useState("idle");
  const [lastMessage, setLastMessage] = useState(null);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;

    const socket = new WebSocket(`${WS_URL}/${channel}?token=${encodeURIComponent(token)}`);

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

