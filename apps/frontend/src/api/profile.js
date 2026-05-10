import { apiClient } from "./client";
import { getAuthOptions } from "./consent";

export function getMyProfile() {
  return apiClient.get("/users/me", getAuthOptions());
}

export function updateMyProfile(payload) {
  return apiClient.patch("/users/me", payload, getAuthOptions());
}
