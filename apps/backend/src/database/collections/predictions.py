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
                        "forecast_year",
                        "forecast_period",
                        "forecast_value",
                        "model",
                        "generated_on",
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
                        "forecast_year": {
                            "bsonType": "int",
                            "description": "Forecast year"
                        },
                        "forecast_period": {
                            "bsonType": "int",
                            "description": "Forecast month (1-12)"
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
                        },
                    }
                }
            },
            validationLevel="strict",
            validationAction="error"
        )
    except Exception as e:
        if "already exists" not in str(e):
            raise

        db.command(
            "collMod",
            "predictions",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "consumer_unit_set_id",
                        "indicator",
                        "forecast_year",
                        "forecast_period",
                        "forecast_value",
                        "model",
                        "generated_on",
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
                        "forecast_year": {
                            "bsonType": "int",
                            "description": "Forecast year"
                        },
                        "forecast_period": {
                            "bsonType": "int",
                            "description": "Forecast month (1-12)"
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
                        },
                    }
                }
            },
            validationLevel="strict",
            validationAction="error",
        )
    
    col = db["predictions"]
    
    # Ensure indexes exist and handle possible conflicts with pre-existing indexes
    desired_indexes = {
        "idx_natural_key": {
            "keys": [("consumer_unit_set_id", ASCENDING), ("indicator", ASCENDING), ("forecast_year", ASCENDING), ("forecast_period", ASCENDING)],
            "unique": True,
        },
        "idx_unit_indicator": {
            "keys": [("consumer_unit_set_id", ASCENDING), ("indicator", ASCENDING)],
            "unique": False,
        },
        "idx_forecast_year_period": {
            "keys": [("forecast_year", ASCENDING), ("forecast_period", ASCENDING)],
            "unique": False,
        },
    }

    existing_indexes = col.index_information()

    for name, index_spec in desired_indexes.items():
        key_spec = index_spec["keys"]
        desired_unique = index_spec["unique"]

        # Rebuild indexes whose fields or uniqueness no longer match the schema contract.
        if name in existing_indexes:
            existing_fields = [t[0] for t in existing_indexes[name]["key"]]
            desired_fields = [t[0] for t in key_spec]
            existing_unique = bool(existing_indexes[name].get("unique", False))
            if existing_fields != desired_fields or existing_unique != desired_unique:
                try:
                    col.drop_index(name)
                except Exception:
                    # best-effort: if drop fails, continue and let create_index raise informative error
                    pass

        create_options = {"name": name, "background": True}
        if desired_unique:
            create_options["unique"] = True

        # If duplicate natural keys already exist, MongoDB rejects this unique index creation.
        col.create_index(key_spec, **create_options)
