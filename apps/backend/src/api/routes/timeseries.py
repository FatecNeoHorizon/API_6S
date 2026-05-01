"""
Time Series Forecasting API endpoints.

Routes for training RandomForest models and generating forecasts for distribution indicators.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from src.control.timeseries_forecast_procedures import TimeSeriesForecastProcedures
from src.etl.query_mongo_timeseries import query_indicators_for_unit
from src.services.retraining_service import schedule_retraining

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/timeseries", tags=["timeseries"])

@router.post("/forecast-unit")
async def forecast_unit_timeseries(
    consumer_unit_set_id: str = Query(..., description="Consumer unit ID (e.g., '16648')"),
    year_start: int = Query(2015, description="Start year for training data"),
    year_end: int = Query(2024, description="End year for training data"),
    indicator_types: Optional[list[str]] = Query(None, description="Indicator types: DEC, FEC, or both"),
    save_models: bool = Query(True, description="Save trained models to disk"),
):
    """
    Generate 12-month forecasts for distribution indicators using RandomForest models.
    
    This endpoint:
    1. Queries MongoDB for DEC/FEC historical data
    2. Trains RandomForest models (80% train, 20% test split)
    3. Evaluates with MAE (Mean Absolute Error)
    4. Generates 12-month forecasts
    5. Returns metrics, forecasts, and model directory
    
    **Parameters:**
    - `consumer_unit_set_id`: Unique identifier for the consumer unit
    - `year_start`: Start year for training data (default: 2015)
    - `year_end`: End year for training data (default: 2024)
    - `indicator_types`: List of indicators to forecast. Options: ["DEC"], ["FEC"], ["DEC", "FEC"]
    - `save_models`: Save trained models as .pkl files for later use
    
    **Response Example:**
    ```json
    {
        "success": true,
        "consumer_unit_id": "16648",
        "metrics": {
            "DEC": {
                "mae": 0.1234,
                "n_train": 115,
                "n_test": 29,
                "n_records": 144
            },
            "FEC": {
                "mae": 0.1567,
                "n_train": 115,
                "n_test": 29,
                "n_records": 144
            }
        },
        "forecasts": [
            {
                "indicator": "DEC",
                "date": "2025-01-01",
                "forecast": 1.2345
            },
            ...
        ],
        "models_directory": "/tmp/models"
    }
    ```
    """
    try:
        # Normalize indicator types
        if indicator_types is None:
            indicator_types = ["DEC", "FEC"]
        
        # Validate indicator types
        valid_indicators = {"DEC", "FEC"}
        invalid = set(indicator_types) - valid_indicators
        if invalid:
            raise ValueError(
                f"Invalid indicator types: {invalid}. Valid options: {valid_indicators}"
            )
        
        # Execute forecast procedure
        procedures = TimeSeriesForecastProcedures()
        result = procedures.forecast_for_unit(
            consumer_unit_set_id=consumer_unit_set_id,
            year_start=year_start,
            year_end=year_end,
            indicator_types=indicator_types,
            save_models=save_models,
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Forecast failed"),
            )
        
        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(exc)}",
        )


@router.get("/forecast-unit/{consumer_unit_set_id}")
async def get_forecast_info(
    consumer_unit_set_id: str,
    year_start: int = Query(2015, description="Start year for reference"),
    year_end: int = Query(2024, description="End year for reference"),
):
    """
    Get metadata about a consumer unit for forecasting.
    
    This endpoint provides information needed before running forecasts:
    - Available indicators (DEC, FEC)
    - Data availability (date range)
    - Number of records
    
    **Parameters:**
    - `consumer_unit_set_id`: Consumer unit ID
    - `year_start`: Start year (default: 2015)
    - `year_end`: End year (default: 2024)
    """
    try:
        from src.etl.query_mongo_timeseries import validate_timeseries_data
        from src.control.distribution_indices_procedures import Distribution_indices_procedures
        
        indicators_available = {}
        
        for indicator in ["DEC", "FEC"]:
            procedures = Distribution_indices_procedures()
            records = procedures.getAll({
                "consumer_unit_set_id": consumer_unit_set_id,
                "indicator_type_code": indicator,
                "year": {"$gte": year_start, "$lte": year_end},
            })
            
            if records:
                indicators_available[indicator] = {
                    "available": True,
                    "record_count": len(records),
                    "date_range": {
                        "start": f"{year_start}-01",
                        "end": f"{year_end}-12",
                    }
                }
            else:
                indicators_available[indicator] = {
                    "available": False,
                    "record_count": 0,
                }
        
        return {
            "consumer_unit_id": consumer_unit_set_id,
            "year_range": {
                "start": year_start,
                "end": year_end,
            },
            "indicators": indicators_available,
            "ready_for_forecast": any(ind["available"] for ind in indicators_available.values()),
        }
    
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching metadata: {str(exc)}",
        )


@router.post("/retrain")
async def trigger_manual_retrain(
    consumer_unit_set_id: str = Query(..., description="Consumer unit ID (e.g., '16648')"),
    year_start: int = Query(2015, description="Start year for retraining data"),
    year_end: int = Query(2024, description="End year for retraining data"),
    indicator_types: Optional[list[str]] = Query(None, description="Indicator types: DEC, FEC, or both"),
):
    """
    Manually trigger model retraining for a consumer unit (async).

    This endpoint trains or retrains RandomForest models for specified indicators
    and immediately returns. Actual training runs in the background.

    **Parameters:**
    - `consumer_unit_set_id`: Consumer unit ID
    - `year_start`: Start year for training data (default: 2015)
    - `year_end`: End year for training data (default: 2024)
    - `indicator_types`: List of indicators to retrain (default: ["DEC", "FEC"])

    **Response:**
    ```json
    {
        "success": true,
        "message": "Retraining scheduled for consumer unit 16648",
        "consumer_unit_id": "16648",
        "indicators": ["DEC", "FEC"]
    }
    ```

    **Note:** Retraining happens in the background. Check logs or re-query the forecast endpoint
    to see updated model metrics.
    """
    try:
        # Normalize indicator types
        if indicator_types is None:
            indicator_types = ["DEC", "FEC"]

        # Validate indicator types
        valid_indicators = {"DEC", "FEC"}
        invalid = set(indicator_types) - valid_indicators
        if invalid:
            raise ValueError(
                f"Invalid indicator types: {invalid}. Valid options: {valid_indicators}"
            )

        # Train and save models for this consumer unit
        # Using a synthetic load_id for manual triggers
        load_id = f"manual_retrain_{consumer_unit_set_id}_{int(__import__('time').time())}"

        procedures = TimeSeriesForecastProcedures()
        result = procedures.forecast_for_unit(
            consumer_unit_set_id=consumer_unit_set_id,
            year_start=year_start,
            year_end=year_end,
            indicator_types=indicator_types,
            save_models=True,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Retraining failed"),
            )

        logger.info(f"Manual retrain triggered for {consumer_unit_set_id}: {load_id}")

        return {
            "success": True,
            "message": f"Retraining completed for consumer unit {consumer_unit_set_id}",
            "consumer_unit_id": consumer_unit_set_id,
            "indicators": indicator_types,
            "metrics": result.get("metrics", {}),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
    except Exception as exc:
        logger.exception(f"Error triggering retrain for {consumer_unit_set_id}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(exc)}",
        )
