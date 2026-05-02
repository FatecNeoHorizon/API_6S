import { apiClient } from "./client";
import { adminClient } from "./adminClient";

export function getTerms() {
  return apiClient.get("/terms");
}

export function getAdminTermsVersions() {
  return adminClient.get("/admin/terms/versions");
}

export function createTermsVersion(payload) {
  return adminClient.post("/admin/terms/versions", payload);
}

export function getVersionClauses(versionId) {
  return adminClient.get(`/admin/terms/versions/${versionId}/clauses`);
}

export function createClause(versionId, payload) {
  return adminClient.post(`/admin/terms/versions/${versionId}/clauses`, payload);
}

export function getAdminPolicyVersion(versionId) {
  return adminClient.get(`/admin/terms/versions/${versionId}`);
}