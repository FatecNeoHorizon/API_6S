# Predictions and Forecasts Implementation Guide

[Back to main README](../README.md#date-sprint-backlog)

### Goal

Document the predictions pipeline end to end so another developer can understand, rerun, and maintain it without opening the original Colab notebook.

### Scope

This document covers:
1. Pipeline architecture from MongoDB data flow to transformation, model training, forecasting, and persistence.
2. Main backend entry points and their responsibilities.
3. Example documents before and after persistence in the `predictions` collection.
4. Manual retraining and validation steps.
5. Traceability between Colab parameters and backend configuration.
6. Minimum checklist to consider the implementation complete.

### Architecture and Data Flow

Main files involved in the pipeline:
1. Data loading and lag preparation: [apps/backend/src/etl/query_mongo_timeseries.py](../apps/backend/src/etl/query_mongo_timeseries.py)
2. Model training and recursive forecasting: [apps/backend/src/control/timeseries_forecast_procedures.py](../apps/backend/src/control/timeseries_forecast_procedures.py)
3. API orchestration and persistence: [apps/backend/src/api/routes/predictions.py](../apps/backend/src/api/routes/predictions.py)
4. Persistence helper with idempotent upsert: [apps/backend/src/etl/load/load_predictions.py](../apps/backend/src/etl/load/load_predictions.py)
5. MongoDB collection schema and indexes: [apps/backend/src/database/collections/predictions.py](../apps/backend/src/database/collections/predictions.py)

Flow overview:
1. The pipeline reads historical DEC/FEC values from MongoDB collection `distribution_indices`.
2. The loader converts `year` + `period` into a monthly date column and sorts the series chronologically.
3. Lag features `lag_1` to `lag_12` are created from the historical values.
4. The model trainer removes rows with incomplete lag windows, trains a `RandomForestRegressor`, and evaluates it with MAE on a chronological holdout slice.
5. The forecasting step runs recursively for 12 months by default: each predicted month is appended to the history and used to forecast the next month.
6. The API route transforms the forecast output into the persistence schema and writes it to MongoDB with upsert semantics.

### Data Loading and Transformation

The loader is implemented in `prepare_timeseries_dataframe()` and `prepare_timeseries()`.

Behavior:
1. Query one consumer unit and one indicator (`DEC` or `FEC`) for the selected year window.
2. Build a normalized dataframe with the monthly anchor column `data` and the target column `VlrIndiceEnviado`.
3. Sort records by time to preserve temporal order.
4. Validate minimum data volume before lag generation.
5. Create lag columns required by the model.

Why this matters:
1. The model uses monthly seasonal memory, so the time order must be preserved.
2. The same shape is used in the Colab and in the backend, which keeps the output comparable.

### Model Training and Forecasting

The trainer lives in `train_forecast_model()`.

Training logic:
1. Build the lag matrix from the prepared dataframe.
2. Remove rows with missing lag values or missing target values.
3. Split chronologically using an 80/20 holdout.
4. Train `RandomForestRegressor(n_estimators=100, n_jobs=-1, random_state=42)`.
5. Measure `mean_absolute_error` on the test slice.

Forecast generation logic:
1. Load the same historical series used for training.
2. Start from the last observed values.
3. Build the lag vector from the most recent history.
4. Predict one month ahead.
5. Append the prediction to the history and repeat until the forecast horizon is reached.

Forecasts for persistence are produced by `generate_forecasts_for_persistence()` and then flattened by the API route.

### Persistence and Deduplication

The saved document schema is defined in [apps/backend/src/model/prediction_model.py](../apps/backend/src/model/prediction_model.py) and enforced by [apps/backend/src/database/collections/predictions.py](../apps/backend/src/database/collections/predictions.py).

Required persisted fields:
1. `consumer_unit_set_id`
2. `indicator`
3. `forecast_year`
4. `forecast_period`
5. `forecast_value`
6. `model`
7. `generated_on`

Deduplication strategy:
1. The persistence helper uses `UpdateOne(..., upsert=True)`.
2. The natural key is composed of:
   - `consumer_unit_set_id`
   - `indicator`
   - `forecast_year`
   - `forecast_period`
3. MongoDB also enforces the same logical key through the `idx_natural_key` index.

This means a rerun of the same forecast window updates the same logical monthly prediction instead of creating a duplicate row.

### Example Documents

Before persistence, the pipeline holds forecast items in memory in the recursive format returned by the trainer:

```json
{
  "consumer_unit_id": "16648",
  "indicator": "DEC",
  "forecast_year": 2025,
  "forecast_period": 1,
  "forecast_value": 1.234
}
```

After persistence, the document stored in MongoDB includes the target month/year plus audit metadata:

```json
{
  "consumer_unit_set_id": "16648",
  "indicator": "DEC",
  "forecast_year": 2025,
  "forecast_period": 1,
  "forecast_value": 1.234,
  "model": "RandomForestRegressor",
  "generated_on": "2025-01-03T10:30:00Z"
}
```

The API response for `GET /predictions/` returns the same persisted shape through the `Prediction` schema.

### Manual Retraining and Re-execution

To rerun the pipeline manually, call the generation endpoint again:

```bash
curl -X POST "http://localhost:8000/predictions/generate?consumer_unit_set_id=16648&indicator_types=DEC&indicator_types=FEC&year_start=2015&year_end=2024"
```

If `consumer_unit_set_id` is omitted, the backend forecasts all consumer units found in `distribution_indices`.

Recommended validation after the call:
1. Check the `202 Accepted` response and save the returned `job_id`.
2. Query saved predictions with:
   ```bash
   curl -s "http://localhost:8000/predictions/?consumer_unit_set_id=16648&indicator=DEC" | jq
   ```
3. Verify MongoDB contains only one logical record per `consumer_unit_set_id + indicator + forecast_year + forecast_period`.
4. Compare the saved values with the expected Colab baseline for the same unit, indicator, and year window.

### Traceability Table

| Colab parameter | Backend location | `.env.backend` / code source | Default value | Notes |
|---|---|---|---|---|
| Forecast horizon | `Settings.model_forecast_months` | `MODEL_FORECAST_MONTHS` | `12` | Controls how many future months are generated and persisted. |
| Training start year | `POST /predictions/generate` and `POST /timeseries/forecast-unit` | Code default in route | `2015` | Not currently environment-driven. Override per request when needed. |
| Training end year | `POST /predictions/generate` and `POST /timeseries/forecast-unit` | Code default in route | `2024` | Not currently environment-driven. Override per request when needed. |
| Indicator list | `indicator_types` query parameter | Code default in route | `DEC`, `FEC` | Not currently environment-driven. |
| Lag window | `prepare_timeseries()` and `train_forecast_model()` | Code default | `12` | Matches the Colab monthly seasonality setup. |
| Minimum records | `prepare_timeseries()` and `train_forecast_model()` | Code default | `20` | Prevents training on sparse series. |
| Random seed | `train_forecast_model()` | Code default | `42` | Keeps the model reproducible for comparisons. |
| Mongo database | `Settings.mongo_db_name` | `MONGO_DB_NAME` | `tecsys` | Used for `distribution_indices` and `predictions`. |

### Validation Checklist

Use this checklist before marking the implementation complete:
1. `POST /predictions/generate` returns `202 Accepted` and a `job_id`.
2. `GET /predictions/` responds with saved documents and supports filtering by unit and indicator.
3. Generated values are compatible with the Colab baseline for the same unit, indicator, and year range.
4. No duplicate logical predictions exist for the same `consumer_unit_set_id + indicator + forecast_year + forecast_period`.
5. MongoDB validates the persisted documents with the `predictions` schema.
6. The forecast horizon matches `MODEL_FORECAST_MONTHS`.
7. The retraining flow can be rerun manually without changing the code path.
8. Logs show inserted/updated/rejected counts for each run.

### Operational Notes

1. The pipeline is asynchronous from the API perspective, so the request returns before the background task finishes.
2. The saved collection is safe to rerun because persistence uses upsert with a natural key.
3. The same route can be used to regenerate a single consumer unit or the whole population.
4. If you need to compare against the original Colab, keep the same training window, lag count, random seed, and forecast horizon.
