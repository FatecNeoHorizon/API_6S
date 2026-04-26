from pymongo import ASCENDING

def setup_tam_sam(db):
    db.create_collection(
        "tam_sam",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "tam_total": {
                        "bsonType": ["int", "long", "null"],
                        "description": "Total count of unique consumer unit sets used to calculate TAM."
                    },
                    "calculated_on": {
                        "bsonType": "date",
                        "description": "Date when the TAM was calculated. Mapped from CalculatedOn."
                    }
                }
            }
        },
        validationLevel="strict",
        validationAction="error"
    )
    db.tam_sam.create_index([("calculated_on", ASCENDING)], name="idx_calculated_on")
    # Exactly one document per metric (tam_total), updated by upsert during recalculation.
    db.tam_sam.create_index([("metric", ASCENDING)], name="ux_metric", unique=True)
