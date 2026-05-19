import { apiClient } from "./client";

export async function getConj(filter) {

  const params = new URLSearchParams(filter)
  let apiData = await apiClient.get(`/geo/conj?${params}`);
  if (apiData) {
    return apiData.features.map(convertConj)
  }
  return null
}

export function convertConj(apiConj) {
  let convertedConj = {
    name: apiConj.properties.name,
    indicator_type_code: apiConj.properties.indicator_type_code,
    year: apiConj.properties.year,
    limit: apiConj.properties.limit,
    accumulated_value: apiConj.properties.accumulated_value,
    periods_count: apiConj.properties.periods_count,
    coordinates: apiConj.geometry.coordinates[0][0],
  }

  return convertedConj;

}