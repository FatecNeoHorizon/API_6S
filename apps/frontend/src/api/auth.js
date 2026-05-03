import { apiClient } from "./client";

export function login(payload) {
  return apiClient.post("/auth/login", payload);
}

export function firstAccess(payload) {
  return apiClient.post("/auth/first-access", payload);
}
