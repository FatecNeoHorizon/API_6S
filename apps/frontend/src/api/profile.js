import { apiClient } from "./client";
import { getAuthOptions } from "./consent";

export function getMyProfile() {
  return apiClient.get("/users/me", getAuthOptions());
}

export function updateMyProfile(payload) {
  return apiClient.patch("/users/me", payload, getAuthOptions());
}

export function exportMyData() {
  return apiClient.get("/auth/me/export", getAuthOptions());
}

export function getMyConsentPreferences(userId) {
  return apiClient.get(`/users/${userId}/consents`, getAuthOptions());
}

export function updateMyConsentPreferences(userId, consents) {
  return apiClient.patch(
    `/users/${userId}/consents`,
    { consents },
    getAuthOptions(),
  );
}