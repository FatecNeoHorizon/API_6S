from pymongo import ASCENDING

def setup_geodatabases(db):
    db.create_collection(
        "geodatabases",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["filename", "load_id", "uploaded_at"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "filename": {
                        "bsonType": "string",
                        "description": "Original GDB filename."
                    },
                    "load_id": {
                        "bsonType": "string",
                        "description": "Reference to load_history.load_id."
                    },
                    "uploaded_at": {
                        "bsonType": "date",
                        "description": "Upload datetime (UTC)."
                    },
                    "distributor": {
                        "bsonType": ["string", "null"],
                        "description": "Distributor name. To be defined in future sprint."
                    },
                    "reference_year": {
                        "bsonType": ["int", "null"],
                        "description": "Reference year of the GDB data. To be defined in future sprint."
                    }
                }
            }
        },
        validationLevel="strict",
        validationAction="error"
    )

    col = db["geodatabases"]

    col.create_index(
        [("load_id", ASCENDING)],
        name="idx_load_id",
        background=True
    )

    col.create_index(
        [("uploaded_at", ASCENDING)],
        name="idx_uploaded_at",
        background=True
    )