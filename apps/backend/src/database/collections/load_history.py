from pymongo import ASCENDING

def setup_load_history(db, collections_exist):
    if "load_history" not in collections_exist:
        db.create_collection(
            "load_history",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "load_id",
                        "collection_name",
                        "batch_version",
                        "started_at",
                        "status",
                    ],
                    "properties": {
                        "_id": {"bsonType": "objectId"},
                        "load_id": {
                            "bsonType": "string",
                            "description": "Unique identifier for one ingestion execution."
                        },
                        "collection_name": {
                            "bsonType": "string",
                            "description": "Target collection loaded in this execution."
                        },
                        "batch_version": {
                            "bsonType": "string",
                            "description": "Version label of the processed batch."
                        },
                        "source_file": {
                            "bsonType": ["string", "null"],
                            "description": "Source file path used in the load."
                        },
                        "started_at": {
                            "bsonType": "date",
                            "description": "Execution start timestamp."
                        },
                        "finished_at": {
                            "bsonType": ["date", "null"],
                            "description": "Execution finish timestamp."
                        },
                        "status": {
                            "bsonType": "string",
                            "enum": ["STARTED", "SUCCESS", "PARTIAL", "ERROR"],
                            "description": "Execution status."
                        },
                        "total_processed": {
                            "bsonType": ["int", "long", "null"],
                            "description": "Total records processed in the execution."
                        },
                        "total_inserted": {
                            "bsonType": ["int", "long", "null"],
                            "description": "Total records inserted in the execution."
                        },
                        "total_updated": {
                            "bsonType": ["int", "long", "null"],
                            "description": "Total records updated in the execution."
                        },
                        "total_rejected": {
                            "bsonType": ["int", "long", "null"],
                            "description": "Total records rejected in the execution."
                        },
                        "chunks_total": {
                            "bsonType": ["int", "null"],
                            "description": "Expected number of chunks for this run."
                        },
                        "chunks_completed": {
                            "bsonType": ["int", "null"],
                            "description": "Number of chunks completed."
                        },
                        "error_message": {
                            "bsonType": ["string", "null"],
                            "description": "Error details when status is ERROR or PARTIAL."
                        }
                    }
                }
            },
            validationLevel="strict",
            validationAction="error"
        )

        col = db["load_history"]
        col.create_index([("load_id", ASCENDING)], unique=True, name="idx_unique_load_id")
        col.create_index([("collection_name", ASCENDING), ("batch_version", ASCENDING)], name="idx_collection_batch")
        col.create_index([("started_at", ASCENDING)], name="idx_started_at")
        col.create_index([("status", ASCENDING)], name="idx_status")
