import { apiClient } from "./client";

export async function getConj(filter) {
  const params = new URLSearchParams(filter)
  let apiData = await apiClient.get(`/geo/conj?${params}`);
  console.log("inside getConj")
  console.log(apiData)
  return apiData.features.map(convertConj)
}

// export function convertGeometry(geometry)
// {
//   return geometry.coordinates[0]
// }

export function convertConj(apiConj)
{
  let convertedConj = {
    name: apiConj.properties.name,
    indicator_type_code: apiConj.properties.indicator_type_code,
    year: apiConj.properties.year,
    limit: apiConj.properties.limit,
    accumulated_value: apiConj.properties.accumulated_value,
    periods_count: apiConj.properties.periods_count,
    coordinates: apiConj.geometry.coordinates[0],
  }

  return convertedConj;

}

// const mockedDataTest = [
//     {
//       name: "ARATEMA",
//       indicator_type_code: "FEC",
//       year: 2012,
//       limit: 7,
//       accumulated_value: 9,
//       periods_count: 8,
//       coordinates: mockedCoordinates,
//     },
//     {
//       name: "TRAVERSE TOWN",
//       indicator_type_code: "DEC",
//       year: 2012,
//       limit: 7,
//       accumulated_value: 5,
//       periods_count: 8,
//       coordinates: mockedCoordinatesTwo,
//     },
//   ]