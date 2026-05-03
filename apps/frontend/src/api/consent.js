import { apiClient } from "./client";

const SESSION_KEYS = [
  "session_uuid",
  "sessionUuid",
  "access_token",
  "accessToken",
  "token",
];

export function getSessionToken() {
  for (const key of SESSION_KEYS) {
    const sessionValue = sessionStorage.getItem(key);
    const localValue = localStorage.getItem(key);

    if (sessionValue) return sessionValue;
    if (localValue) return localValue;
  }

  return null;
}

function getAuthOptions() {
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