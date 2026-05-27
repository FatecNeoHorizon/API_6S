import { apiClient } from "./client";

export function login(payload) {
  return apiClient.post("/auth/login", payload);
}

export function refreshToken(payload) {
  return apiClient.post("/auth/refresh", payload);
}

export function forgotPassword(payload) {
  return apiClient.post("/auth/forgot-password", payload);
}

export function resetPassword(payload) {
  return apiClient.post("/auth/reset-password", payload);
}

export function firstAccess(payload) {
  return apiClient.post("/auth/first-access", payload);
}

function generateCodeVerifier() {
  const array = new Uint8Array(64)
  crypto.getRandomValues(array)
  return btoa(String.fromCharCode(...array))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=/g, "")
}

async function generateCodeChallenge(verifier) {
  const encoder = new TextEncoder()
  const data = encoder.encode(verifier)
  const digest = await crypto.subtle.digest("SHA-256", data)
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=/g, "")
}

function generateState() {
  const array = new Uint8Array(16)
  crypto.getRandomValues(array)
  return btoa(String.fromCharCode(...array))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=/g, "")
}

export async function initiateOAuthLogin() {
  const verifier  = generateCodeVerifier()
  const challenge = await generateCodeChallenge(verifier)
  const state     = generateState()

  sessionStorage.setItem("pkce_verifier", verifier)
  sessionStorage.setItem("pkce_state",    state)

  const params = new URLSearchParams({
    client_id:             "zeus-frontend",
    redirect_uri:          `${window.location.origin}/auth/callback`,
    response_type:         "code",
    scope:                 "openid profile email",
    code_challenge:        challenge,
    code_challenge_method: "S256",
    state,
  })

  return `${import.meta.env.VITE_KEYCLOAK_URL}/realms/zeus/protocol/openid-connect/auth?${params}`
}