const TOKEN_KEY = "fitness_os_token";
const REFRESH_TOKEN_KEY = "fitness_os_refresh_token";
const USER_KEY = "fitness_os_user";

function safeLocalStorage() {
  if (typeof window === "undefined") return;
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

export function saveAuthSession(token, refreshToken, user) {
  const storage = safeLocalStorage();
  if (!storage) return;
  storage.setItem(TOKEN_KEY, token);
  storage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  storage.setItem(USER_KEY, JSON.stringify(user));
}

export function getAccessToken() {
  const storage = safeLocalStorage();
  return storage?.getItem(TOKEN_KEY) || null;
}

export function getRefreshToken() {
  const storage = safeLocalStorage();
  return storage?.getItem(REFRESH_TOKEN_KEY) || null;
}

export function getStoredUser() {
  const storage = safeLocalStorage();
  const rawUser = storage?.getItem(USER_KEY);
  if (!rawUser) return null;
  try {
    return JSON.parse(rawUser);
  } catch {
    clearAuthSession();
    return null;
  }
}

export function clearAuthSession() {
  const storage = safeLocalStorage();
  if (!storage) return;
  storage.removeItem(TOKEN_KEY);
  storage.removeItem(REFRESH_TOKEN_KEY);
  storage.removeItem(USER_KEY);
}
