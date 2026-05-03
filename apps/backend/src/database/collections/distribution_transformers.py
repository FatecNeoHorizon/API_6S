from pymongo import ASCENDING

"""
Example Document:
{
    "_id": "ObjectId('69e3b182218b5f69b67bd0bf')",
    "code": "TR-001-A",
    "distributor_code": "001",
    "description": "Transformador Centro A",
    "status": "SM",
    "location_area": "1",
    "nominal_power_kva": 500.0,
    "iron_losses_kw": 45.0,
    "copper_losses_kw": 60.0,
    "substation": "SE-001"
}
"""

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
                    },
                    "substation": {
                        "bsonType": "string",
                        "description": "Substation code this transformer belongs to. Foreign key to substations.code. Mapped from ETL."
                    }
                }
            }
        },
        validationLevel="strict",
        validationAction="error"
    )

    col = db["distribution_transformers"]

    col.create_index(
        [("code", ASCENDING)],
        unique=True,
        name="idx_unique_code",
        background=True
    )

    col.create_index(
        [("distributor_code", ASCENDING)],
        name="idx_distributor",
        background=True
    )

    col.create_index(
        [("location_area", ASCENDING)],
        name="idx_location_area",
        background=True
    )

    col.create_index([("nominal_power_kva", ASCENDING)], name="idx_power", background=True)

    col.create_index(
        [("substation", ASCENDING)],
        name="idx_substation",
        background=True
    )