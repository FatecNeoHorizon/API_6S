from pydantic import BaseModel
from datetime import datetime


class Prediction(BaseModel):
    """MongoDB prediction document schema."""
    consumer_unit_set_id: str
    indicator: str
    forecast_date: str  # "YYYY-MM-DD"
    forecast_value: float
    model: str  # e.g., "RandomForestRegressor"
    generated_on: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "consumer_unit_set_id": "16648",
                "indicator": "DEC",
                "forecast_date": "2025-01-01",
                "forecast_value": 1.234,
                "model": "RandomForestRegressor",
                "generated_on": "2025-01-03T10:30:00Z"
            }
        }
