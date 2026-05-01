const ADMIN_SESSION_TOKEN_KEY = "admin_session_token";
const DEV_ADMIN_SESSION_TOKEN = "fdd08bdb-c252-4c55-9948-5a8b77e88556";

export function getAdminSessionToken() {
  if (!globalThis.window) {
    return null;
  }

  return localStorage.getItem(ADMIN_SESSION_TOKEN_KEY) || DEV_ADMIN_SESSION_TOKEN;
}

export function setAdminSessionToken(token) {
  localStorage.setItem(ADMIN_SESSION_TOKEN_KEY, token);
}

export function clearAdminSessionToken() {
  localStorage.removeItem(ADMIN_SESSION_TOKEN_KEY);
}