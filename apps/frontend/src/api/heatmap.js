import { apiClient } from "./client";

export function getConj(filter) {
  const params = new URLSearchParams(filter)
  return apiClient.get(`/geo/conj?${params}`);
}