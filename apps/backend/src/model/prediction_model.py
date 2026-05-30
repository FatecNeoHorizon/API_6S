from datetime import datetime
from typing import Any

from pydantic import BaseModel


class Prediction(BaseModel):
    """MongoDB prediction document schema."""
    consumer_unit_set_id: str
    indicator: str
    forecast_year: int
    forecast_period: int  # 1-12
    forecast_value: float
    model: str  # e.g., "RandomForestRegressor"
    generated_on: datetime
    validation_metrics: dict[str, Any] | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "consumer_unit_set_id": "16648",
                "indicator": "DEC",
                "forecast_year": 2025,
                "forecast_period": 1,
                "forecast_value": 1.234,
                "model": "RandomForestRegressor",
                "generated_on": "2025-01-03T10:30:00Z",
                "validation_metrics": {
                    "success": True,
                    "mae": 0.2278,
                    "n_train": 80,
                    "n_test": 20,
                    "n_records": 100
                }
            }
        }
