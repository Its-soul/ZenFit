function publicUrl(name, configuredValue, developmentDefault, protocols) {
  const value = configuredValue || (process.env.NODE_ENV === "development" ? developmentDefault : "");
  if (!value) {
    throw new Error(`${name} must be configured outside development`);
  }
  let parsed;
  try {
    parsed = new URL(value);
  } catch {
    throw new Error(`${name} must be an absolute URL`);
  }
  if (!protocols.includes(parsed.protocol)) {
    throw new Error(`${name} must use ${protocols.join(" or ")}`);
  }
  if (process.env.NODE_ENV === "production" && ["localhost", "127.0.0.1"].includes(parsed.hostname)) {
    throw new Error(`${name} cannot target localhost in production`);
  }
  return value.replace(/\/$/, "");
}

export const API_URL = publicUrl(
  "NEXT_PUBLIC_API_URL",
  process.env.NEXT_PUBLIC_API_URL,
  "http://localhost:8000/api/v1",
  ["http:", "https:"]
);

export const WS_URL = publicUrl(
  "NEXT_PUBLIC_WS_URL",
  process.env.NEXT_PUBLIC_WS_URL,
  "ws://localhost:8000/ws",
  process.env.NODE_ENV === "production" ? ["wss:"] : ["ws:", "wss:"]
);
