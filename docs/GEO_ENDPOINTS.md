# Geographic Endpoints (CONJ / Heatmap)

This document describes the backend endpoints that power the geographic heatmap feature (US11). Data comes from the `conj` MongoDB collection, which stores electrical set (Conjunto) records with their geometries and annual DEC/FEC indicator summaries.

---

## MongoDB Collection: `conj`

Each document represents one electrical set (conjunto elétrico) and contains:

| Field | Type | Description |
|:---|:---|:---|
| `code` | string | Unique conjunto identifier (e.g. distributor + set code) |
| `name` | string | Human-readable conjunto name |
| `geometry` | GeoJSON object | Polygon or MultiPolygon geometry for the set boundary |
| `annual_summaries` | array | One entry per year × indicator type |

Each `annual_summaries` entry:

| Field | Type | Description |
|:---|:---|:---|
| `year` | int | Reference year |
| `indicator_type_code` | `"DEC"` or `"FEC"` | Indicator type |
| `limit` | float | Regulatory limit for this indicator |
| `accumulated_value` | float | Accumulated DEC or FEC value for the year |
| `periods_count` | int | Number of measurement periods included |
| `criticality` | string | Derived criticality label (e.g. `"HIGH"`, `"MEDIUM"`, `"LOW"`) |

---

## Endpoints

### `GET /conj`

Returns all CONJ documents that have a valid geometry as a **GeoJSON FeatureCollection**. Optionally filtered by year and/or indicator type.

**Authentication:** Required (`get_current_user`)

**Query parameters:**

| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `year` | int (1900–2100) | No | Filter to summaries for a specific year |
| `indicator_type_code` | `"DEC"` or `"FEC"` | No | Filter to a specific indicator type |

**Response (`200 OK`):** GeoJSON FeatureCollection

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lng, lat], ...]]
      },
      "properties": {
        "code": "COELBA-001",
        "name": "Conjunto Nordeste I",
        "indicator_type_code": "DEC",
        "year": 2023,
        "limit": 10.5,
        "accumulated_value": 8.3,
        "periods_count": 12
      }
    }
  ]
}
```

**Filtering behavior:**
- If neither `year` nor `indicator_type_code` is provided, the first `annual_summaries` entry is used for each document.
- If either filter is provided, documents without a matching summary are **excluded** from the response.
- Documents without a valid `geometry` (missing, null, or lacking `type`/`coordinates`) are always skipped.

**Errors:**
- `500` — internal error reading the `conj` collection

---

### `PUT /update-conj`

Updates a specific CONJ document's `name` and/or one `annual_summaries[n].accumulated_value` by MongoDB `_id`.

> This endpoint is intended for administrative data corrections. It modifies live analytical data directly.

**Authentication:** Required (`get_current_user`)

**Query parameters:**

| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `id` | string | No | MongoDB `_id` of the document to update (24-char hex) |
| `update_index` | int | No | Index of the `annual_summaries` array entry to update |
| `new_value` | float | No | New value for `annual_summaries[update_index].accumulated_value` |
| `new_name` | string | No | New value for `name` |

**Response (`200 OK`):** The previous document (before update), as returned by `find_one_and_update`.

**Errors:**
- `500` — invalid `_id` format or internal error updating the collection

---

## How the Heatmap Uses This Data

The frontend (`/heatmap`) calls `GET /conj` with a `year` and `indicator_type_code` filter selected by the user. The returned GeoJSON FeatureCollection is rendered on an interactive Brazil map where each set's polygon is colored by `accumulated_value` relative to `limit` or by derived criticality.

The heatmap supports four view modes via tabs: **DEC**, **FEC**, **Losses**, **Criticality**.

---

## Related Documents

| Document | Relationship |
|:---|:---|
| [UI_DESIGN.md](UI_DESIGN.md) | Heatmap screen components and user interactions |
| [NON_RELATIONAL_DATABASE.md](NON_RELATIONAL_DATABASE.md) | MongoDB schema for the `conj` collection |
| [BACKEND_INFRASTRUCTURE.md](BACKEND_INFRASTRUCTURE.md) | Backend architecture and ETL pipeline context |

---

*Last updated: 05/31/2026*
