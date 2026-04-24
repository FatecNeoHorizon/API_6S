from pymongo import ASCENDING

def setup_substations(db):
    db.create_collection(
        "substations",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["code", "distributor_code"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "code": {
                        "bsonType": "string",
                        "description": "Unique substation identifier. Mapped from COD_ID."
                    },
                    "distributor_code": {
                        "bsonType": ["string", "null"],
                        "description": "Distributor code. Mapped from DIST."
                    },
                    "description": {
                        "bsonType": ["string", "null"],
                        "description": "Substation description. Mapped from DESCR."
                    }
                }
            }
        },
        validationLevel="strict",
        validationAction="error"
    )

    col = db["substations"]
    col.create_index([("code", ASCENDING)], unique=True, name="idx_unique_code")
    col.create_index([("distributor_code", ASCENDING)], name="idx_distributor")