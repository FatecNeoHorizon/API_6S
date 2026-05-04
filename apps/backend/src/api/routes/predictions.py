from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timezone
import logging
import uuid

from src.control.timeseries_forecast_procedures import TimeSeriesForecastProcedures
from src.etl.load.load_predictions import persist_predictions
from src.model.prediction_model import Prediction
from src.config.settings import Settings
from src.database.connection import get_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predictions", tags=["predictions"])


def get_all_consumer_units() -> List[str]:
    """
    Query MongoDB for all unique consumer_unit_set_id values in distribution_indices collection.
    
    Returns:
        List of unique consumer unit IDs, or empty list if none found.
    """
    try:
        settings = Settings()
        client = get_client()
        db = client[settings.mongo_db_name]
        collection = db["distribution_indices"]
        
        units = collection.distinct("consumer_unit_set_id")
        logger.info(f"[get_all_consumer_units] Found {len(units)} unique consumer units")
        return units
    except Exception as exc:
        logger.exception("[get_all_consumer_units] Error querying consumer units: %s", exc)
        return []


def generate_predictions_task(
    consumer_unit_set_id: Optional[str] = None,
    indicator_types: Optional[List[str]] = None,
    year_start: int = 2015,
    year_end: int = 2024,
) -> None:
    """
    Background task to generate and persist predictions for consumer units.
    
    If consumer_unit_set_id is None, forecasts all unique units in the database.
    If specified, forecasts only that unit.
    
    Args:
        consumer_unit_set_id: Specific unit to forecast, or None for all units
        indicator_types: List of indicators ("DEC", "FEC"), defaults to both
        year_start: Start year for training data
        year_end: End year for training data
    """
    if indicator_types is None:
        indicator_types = ["DEC", "FEC"]
    
    try:
        settings = Settings()
        client = get_client()
        db = client[settings.mongo_db_name]
        predictions_collection = db["predictions"]
        
        # Allow the endpoint to target one unit or the full population discovered in MongoDB.
        units_to_process = []
        if consumer_unit_set_id:
            units_to_process = [consumer_unit_set_id]
        else:
            units_to_process = get_all_consumer_units()
        
        if not units_to_process:
            logger.warning("[generate_predictions_task] No consumer units found to forecast")
            return
        
        logger.info(f"[generate_predictions_task] Starting forecast for {len(units_to_process)} units")
        
        procedures = TimeSeriesForecastProcedures(connection=client)
        total_inserted = 0
        total_updated = 0
        failed_units = []
        
        # Process each unit independently so a failure does not stop the rest of the batch.
        for unit_id in units_to_process:
            try:
                logger.info(f"[generate_predictions_task] Forecasting unit {unit_id}")
                
                result = procedures.forecast_for_unit(
                    consumer_unit_set_id=unit_id,
                    year_start=year_start,
                    year_end=year_end,
                    indicator_types=indicator_types,
                    save_models=True,
                )
                
                if not result.get("success"):
                    logger.warning(
                        f"[generate_predictions_task] Forecast failed for {unit_id}: {result.get('message')}"
                    )
                    failed_units.append(unit_id)
                    continue
                
                # Adapt the forecasting output to the exact document shape stored in predictions.
                all_predictions = []
                for forecast in result.get("forecasts", []):
                    pred = {
                        "consumer_unit_set_id": forecast.get("consumer_unit_id"),
                        "indicator": forecast.get("indicator"),
                        "forecast_year": forecast.get("forecast_year"),
                        "forecast_period": forecast.get("forecast_period"),
                        "forecast_value": forecast.get("forecast_value"),
                        "model": "RandomForestRegressor",
                        "generated_on": datetime.now(timezone.utc),
                    }
                    all_predictions.append(pred)
                
                if all_predictions:
                    # Upsert on the natural key so reruns update the same logical month instead of duplicating it.
                    persist_metrics = persist_predictions(predictions_collection, all_predictions)
                    total_inserted += persist_metrics.get("inserted", 0)
                    total_updated += persist_metrics.get("updated", 0)
                    logger.info(
                        f"[generate_predictions_task] Unit {unit_id}: "
                        f"Inserted {persist_metrics.get('inserted', 0)}, "
                        f"Updated {persist_metrics.get('updated', 0)}"
                    )
                
            except Exception as exc:
                logger.exception(f"[generate_predictions_task] Error forecasting unit {unit_id}: %s", exc)
                failed_units.append(unit_id)
        
        logger.info(
            f"[generate_predictions_task] Completed. "
            f"Total inserted: {total_inserted}, updated: {total_updated}, "
            f"failed units: {len(failed_units)}"
        )
        
        if failed_units:
            logger.warning(f"[generate_predictions_task] Failed units: {failed_units}")
    
    except Exception as exc:
        logger.exception("[generate_predictions_task] Background task failed: %s", exc)


@router.post("/generate", status_code=202)
async def generate_predictions(
    background_tasks: BackgroundTasks,
    consumer_unit_set_id: Optional[str] = Query(
        None,
        description="Specific consumer unit ID to forecast (e.g., '16648'). If None, forecasts all units."
    ),
    indicator_types: Optional[List[str]] = Query(
        None,
        description="Indicator types to forecast: 'DEC', 'FEC', or both. Defaults to both."
    ),
    year_start: int = Query(2015, description="Start year for training data"),
    year_end: int = Query(2024, description="End year for training data"),
):
    """
    Trigger prediction generation and persistence in the background.
    
    This endpoint accepts optional filtering parameters and schedules a background task
    to generate and persist predictions. Returns immediately with a job_id.
    
    **Parameters:**
    - `consumer_unit_set_id` (optional): Forecast only this consumer unit. If omitted, forecasts all units.
    - `indicator_types` (optional): List of indicators to forecast (default: ["DEC", "FEC"])
    - `year_start` (optional): Start year for training data (default: 2015)
    - `year_end` (optional): End year for training data (default: 2024)
    
    **Response (HTTP 202 Accepted):**
    ```json
    {
        "status": "STARTED",
        "job_id": "<uuid>",
        "consumer_unit_set_id": "16648 or null",
        "indicator_types": ["DEC", "FEC"],
        "year_range": "2015-2024"
    }
    ```
    
    **Note:** The job runs asynchronously in the background. Check the GET /predictions endpoint
    to query saved predictions and verify results.
    """
    try:
        # Normalize and validate indicator types
        if indicator_types is None:
            indicator_types = ["DEC", "FEC"]
        
        valid_indicators = {"DEC", "FEC"}
        invalid = set(indicator_types) - valid_indicators
        if invalid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid indicator types: {invalid}. Valid options: {valid_indicators}"
            )
        
        # Generate job ID
        job_id = uuid.uuid4().hex
        
        # Schedule background task
        background_tasks.add_task(
            generate_predictions_task,
            consumer_unit_set_id=consumer_unit_set_id,
            indicator_types=indicator_types,
            year_start=year_start,
            year_end=year_end,
        )
        
        logger.info(
            f"[generate_predictions] Forecast scheduled - job_id: {job_id}, "
            f"unit: {consumer_unit_set_id or 'all'}, "
            f"indicators: {indicator_types}"
        )
        
        return {
            "status": "STARTED",
            "job_id": job_id,
            "consumer_unit_set_id": consumer_unit_set_id,
            "indicator_types": indicator_types,
            "year_range": f"{year_start}-{year_end}",
        }
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("[generate_predictions] Error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while scheduling prediction generation"
        )


@router.get("/", response_model=dict)
async def get_predictions(
    consumer_unit_set_id: Optional[str] = Query(
        None,
        description="Filter by consumer unit ID (e.g., '16648')"
    ),
    indicator: Optional[str] = Query(
        None,
        description="Filter by indicator type: 'DEC' or 'FEC'"
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip (pagination)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return (default: 100, max: 1000)"),
):
    """
    Query saved predictions from the database with optional filtering.
    
    Returns predictions with optional filters by consumer unit and indicator type.
    Results are sorted by generation date (newest first) and paginated.
    
    **Parameters:**
    - `consumer_unit_set_id` (optional): Filter by consumer unit ID
    - `indicator` (optional): Filter by indicator type ('DEC' or 'FEC')
    - `skip` (optional): Pagination offset (default: 0)
    - `limit` (optional): Pagination limit (default: 100, max: 1000)
    
    **Response:**
    ```json
    {
        "total": 150,
        "skip": 0,
        "limit": 100,
        "predictions": [
            {
                "consumer_unit_set_id": "16648",
                "indicator": "DEC",
                "forecast_year": 2025,
                "forecast_period": 1,
                "forecast_value": 1.234,
                "model": "RandomForestRegressor",
                "generated_on": "2025-01-03T10:30:00Z"
            },
            ...
        ]
    }
    ```
    
    **Query Examples:**
    - Get all predictions: `GET /predictions/`
    - Filter by unit: `GET /predictions/?consumer_unit_set_id=16648`
    - Filter by unit and indicator: `GET /predictions/?consumer_unit_set_id=16648&indicator=DEC`
    - Pagination: `GET /predictions/?skip=100&limit=50`
    """
    try:
        settings = Settings()
        client = get_client()
        db = client[settings.mongo_db_name]
        predictions_collection = db["predictions"]
        
        # Build filter dict (only include non-None values)
        filter_dict = {}
        if consumer_unit_set_id is not None:
            filter_dict["consumer_unit_set_id"] = consumer_unit_set_id
        if indicator is not None:
            filter_dict["indicator"] = indicator
        
        # Query with pagination
        cursor = predictions_collection.find(filter_dict).sort(
            "generated_on", -1  # Sort by generated_on descending (newest first)
        ).skip(skip).limit(limit)
        
        # Convert to list and count total
        predictions_list = list(cursor)
        
        # Get total count (with filter but without pagination)
        total_count = predictions_collection.count_documents(filter_dict)
        
        # Convert MongoDB documents to Pydantic models
        predictions = []
        for doc in predictions_list:
            # Remove MongoDB's _id field for cleaner response
            if "_id" in doc:
                del doc["_id"]
            try:
                predictions.append(Prediction(**doc))
            except Exception as exc:
                logger.warning(f"[get_predictions] Failed to parse prediction document: {exc}")
                continue
        
        logger.info(
            f"[get_predictions] Returned {len(predictions)} predictions "
            f"(total: {total_count}, filters: {filter_dict})"
        )
        
        return {
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "predictions": predictions,
        }
    
    except Exception as exc:
        logger.exception("[get_predictions] Error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while querying predictions"
        )
