import { apiClient } from "./client";

export function getTerms() {
  return apiClient.get("/terms");
}