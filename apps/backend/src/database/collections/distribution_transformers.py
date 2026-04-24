from pymongo import ASCENDING

def setup_distribution_transformers(db):
    db.create_collection(
        "distribution_transformers",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["code", "distributor_code"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "code": {
                        "bsonType": "string",
                        "description": "Unique transformer identifier. Mapped from COD_ID."
                    },
                    "distributor_code": {
                        "bsonType": ["string", "null"],
                        "description": "Distributor code. Mapped from DIST."
                    },
                    "description": {
                        "bsonType": ["string", "null"],
                        "description": "Transformer description. Mapped from DESCR."
                    },
                    "status": {
                        "bsonType": ["string", "null"],
                        "description": "Operational status. Mapped from SIT_ATIV."
                    },
                    "location_area": {
                        "bsonType": ["string", "null"],
                        "enum": ["1", "2", None],
                        "description": "Location area: 1 = Urban, 2 = Rural. Mapped from ARE_LOC."
                    },
                    "nominal_power_kva": {
                        "bsonType": ["double", "null"],
                        "description": "Nominal power in kVA. Mapped from POT_NOM."
                    },
                    "iron_losses_kw": {
                        "bsonType": ["double", "null"],
                        "description": "Iron (no-load) losses in kW. Mapped from PER_FER."
                    },
                    "copper_losses_kw": {
                        "bsonType": ["double", "null"],
                        "description": "Copper (load) losses in kW. Mapped from PER_COB."
                    }
                }
            }
        },
        validationLevel="moderate",
        validationAction="error"
    )

    col = db["distribution_transformers"]
    col.create_index([("code", ASCENDING)], unique=True, name="idx_unique_code")
    col.create_index([("distributor_code", ASCENDING)], name="idx_distributor")
    col.create_index([("location_area", ASCENDING)], name="idx_location_area")
    col.create_index([("nominal_power_kva", ASCENDING)], name="idx_power")