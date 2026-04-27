## TAM Implementation Guide

[Back to main README](../README.md#date-sprint-backlog)

### Goal

Document how TAM is calculated, persisted, reprocessed, and validated so any developer can debug and rerun the flow without verbal context.

### Scope

This document covers:
1. Data flow from `distribution_indices` to `tam_sam`.
2. Deduplication and idempotency strategy.
3. Example records and expected outputs.
4. Manual reprocessing instructions.
5. Traceability mapping.
6. Validation checklist for QA.

### Architecture and Data Flow

Main files:
1. Loader and persistence of indicators: `apps/backend/src/etl/load/load_decfec.py`
2. TAM calculation and Mongo persistence: `apps/backend/src/control/tam_sam_procedures.py`
3. TAM API routes: `apps/backend/src/api/routes/tam_sam.py`
4. TAM collection schema and indexes: `apps/backend/src/database/collections/tam_sam.py`

Flow:
1. CSV DECFEC is processed in chunks and transformed.
2. Rows are written to `distribution_indices` with `UpdateOne(..., upsert=True)` using the natural key:
   - `agent_acronym`
   - `consumer_unit_set_id`
   - `indicator_type_code`
   - `year`
   - `period`
3. At the end of load, TAM is recalculated with aggregation:
   - ignore `consumer_unit_set_id` in `[null, ""]`
   - group by distinct `consumer_unit_set_id`
   - count total groups as `tam_total`
4. Result is persisted in `tam_sam` with `update_one(..., upsert=True)` and fixed selector `{ "metric": "tam_total" }`.
5. Frontend reads value from `GET /tam-sam/tam`.

### Deduplication Logic

Indicators (`distribution_indices`):
1. Loader uses upsert with a natural key to avoid duplicate measurements in reprocessing.
2. Collection also has unique index `idx_unique_measurement` on that same key.

TAM (`tam_sam`):
1. TAM persistence uses upsert by `{ "metric": "tam_total" }`.
2. Collection has unique index `ux_metric` on `metric`, enforcing one logical TAM document.

### Sample Data (Raw and Final)

Sample records from `distribution_indices` used in TAM calculation:

```json
[
  {
    "agent_acronym": "TST",
    "consumer_unit_set_id": "0001",
    "indicator_type_code": "DEC",
    "year": 2025,
    "period": 1,
    "value": 1.0
  },
  {
    "agent_acronym": "TST",
    "consumer_unit_set_id": "0001",
    "indicator_type_code": "FEC",
    "year": 2025,
    "period": 1,
    "value": 0.5
  },
  {
    "agent_acronym": "TST",
    "consumer_unit_set_id": "0002",
    "indicator_type_code": "DEC",
    "year": 2025,
    "period": 1,
    "value": 1.0
  },
  {
    "agent_acronym": "TST",
    "consumer_unit_set_id": "0003",
    "indicator_type_code": "DEC",
    "year": 2025,
    "period": 1,
    "value": 1.0
  }
]
```

Distinct `consumer_unit_set_id` in sample: `0001`, `0002`, `0003`.
Expected TAM for this sample: `3`.

Final persisted document in `tam_sam`:

```json
{
  "metric": "tam_total",
  "tam_total": 3,
  "calculated_on": "2026-04-25T10:00:00Z"
}
```

### Manual Reprocessing

Prerequisites:
1. Backend and Mongo running.
2. `CSV_FILE_PATH` set correctly in backend env.

Steps:
1. Process indicators:
```bash
curl -s http://localhost:8000/process-decfec | jq
```
2. Recalculate TAM:
```bash
curl -s -X POST http://localhost:8000/tam-sam/calculate | jq
```
3. Read TAM for frontend:
```bash
curl -s http://localhost:8000/tam-sam/tam | jq
```

Consistency checks after reprocessing:
1. `tam_total` is deterministic for same dataset.
2. `calculated_on` changes on each run.
3. No duplicate TAM docs:
```javascript
db.tam_sam.countDocuments({ metric: "tam_total" }) // expected: 1
```

### Traceability Table

| Source Collection | Source Field | Transformation Rule | Target Collection | Target Field |
|---|---|---|---|---|
| distribution_indices | consumer_unit_set_id | Distinct count, ignoring null/empty | tam_sam | tam_total |
| system clock (UTC) | n/a | Current UTC timestamp at calculation time | tam_sam | calculated_on |

### Validation Checklist

1. Unique index validation:
```javascript
db.distribution_indices.getIndexes().find(i => i.name === "idx_unique_measurement")
db.tam_sam.getIndexes().find(i => i.name === "ux_metric")
```
2. Null/empty gap validation in source field:
```javascript
db.distribution_indices.countDocuments({ consumer_unit_set_id: { $in: [null, ""] } })
```
3. Distinct count from indicators (ground truth for TAM):
```javascript
db.distribution_indices.aggregate([
  { $match: { consumer_unit_set_id: { $nin: [null, ""] } } },
  { $group: { _id: "$consumer_unit_set_id" } },
  { $count: "tam_total" }
])
```
4. Compare with TAM API result:
```bash
curl -s http://localhost:8000/tam-sam/tam | jq
```
5. Compare with GDB CONJ reference count (when applicable in test data):
   - Expected: same number of unique sets used for TAM validation scenario.

### Debug Tips

1. If `GET /tam-sam/tam` returns 404, execute `POST /tam-sam/calculate` first.
2. If TAM diverges from expected count, inspect null/empty `consumer_unit_set_id` and type formatting differences (for example `0012` vs `12`).
3. If reprocessing creates duplicates, validate both upsert selector and unique index `ux_metric`.

### API Contract

1. `POST /tam-sam/calculate`
   - Trigger recalculation and persistence.
   - Returns `{ tam_total, calculated_on }`.
2. `GET /tam-sam/tam`
   - Returns last persisted TAM.
   - Returns 404 when TAM was not calculated yet.
