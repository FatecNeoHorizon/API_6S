import { apiClient } from "./client";

export function login(payload) {
  return apiClient.post("/auth/login", payload);
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
