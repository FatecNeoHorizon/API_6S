from pymongo import ASCENDING


def setup_predictions(db):
    """Create and configure the predictions collection."""
    try:
        db.create_collection(
            "predictions",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "consumer_unit_set_id",
                        "indicator",
                        "forecast_date",
                        "forecast_value",
                        "model",
                        "generated_on"
                    ],
                    "properties": {
                        "_id": {"bsonType": "objectId"},
                        "consumer_unit_set_id": {
                            "bsonType": "string",
                            "description": "Identifier of the consumer unit set"
                        },
                        "indicator": {
                            "bsonType": "string",
                            "description": "Indicator type (e.g., 'DEC' or 'FEC')"
                        },
                        "forecast_date": {
                            "bsonType": "string",
                            "description": "Forecast date in YYYY-MM-DD format"
                        },
                        "forecast_value": {
                            "bsonType": "double",
                            "description": "Predicted value"
                        },
                        "model": {
                            "bsonType": "string",
                            "description": "Model name/version used for prediction"
                        },
                        "generated_on": {
                            "bsonType": "date",
                            "description": "Timestamp when prediction was generated"
                        }
                    }
                }
            },
            validationLevel="strict",
            validationAction="error"
        )
    except Exception as e:
        if "already exists" not in str(e):
            raise
    
    col = db["predictions"]
    
    # Natural key index for upsert idempotency
    col.create_index(
        [
            ("consumer_unit_set_id", ASCENDING),
            ("indicator", ASCENDING),
            ("forecast_date", ASCENDING)
        ],
        name="idx_natural_key",
        background=True
    )
    
    # Index for querying predictions by unit and indicator
    col.create_index(
        [
            ("consumer_unit_set_id", ASCENDING),
            ("indicator", ASCENDING)
        ],
        name="idx_unit_indicator",
        background=True
    )
    
    # Index for querying by forecast date
    col.create_index(
        [("forecast_date", ASCENDING)],
        name="idx_forecast_date",
        background=True
    )
