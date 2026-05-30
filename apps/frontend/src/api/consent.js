import { apiClient } from "./client";

const ACCESS_TOKEN_KEYS = [
  "session_uuid",
  "sessionUuid",
  "access_token",
  "accessToken",
  "token",
];

const REFRESH_TOKEN_KEYS = [
  "refresh_token",
  "refreshToken",
];

const SESSION_KEYS = [...ACCESS_TOKEN_KEYS, ...REFRESH_TOKEN_KEYS];

function getStoredValue(keys) {
  for (const key of keys) {
    const sessionValue = sessionStorage.getItem(key);
    const localValue = localStorage.getItem(key);

    if (sessionValue) return sessionValue;
    if (localValue) return localValue;
  }

  return null;
}

export function getSessionToken() {
  return getStoredValue(ACCESS_TOKEN_KEYS);
}

export function getRefreshToken() {
  return getStoredValue(REFRESH_TOKEN_KEYS);
}

export function getAuthOptions() {
  const token = getSessionToken();

  if (!token) {
    return {};
  }

  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
}

export function saveClientSession(token, { remember = false, refreshToken = null } = {}) {
  // Clear old tokens from both storages first
  for (const key of SESSION_KEYS) {
    sessionStorage.removeItem(key);
    localStorage.removeItem(key);
  }

  // Save the new token to the appropriate storage
  const storage = remember ? localStorage : sessionStorage;
  storage.setItem("access_token", token);
  storage.setItem("accessToken", token);

  if (refreshToken) {
    storage.setItem("refresh_token", refreshToken);
    storage.setItem("refreshToken", refreshToken);
  }
}

export function clearClientSession() {
  for (const key of SESSION_KEYS) {
    sessionStorage.removeItem(key);
    localStorage.removeItem(key);
  }
}

export function getPendingConsent() {
  return apiClient.get("/consent/pending", getAuthOptions());
}

export function submitConsent(actions) {
  return apiClient.post("/consent", { actions }, getAuthOptions());
}

export async function logoutUser() {
  try {
    await apiClient.post("/auth/logout", {}, getAuthOptions());
  } catch {
    // Logout must still clean the local session even if the backend logout route
    // is unavailable or the session is already expired.
  } finally {
    clearClientSession();
  }
}
