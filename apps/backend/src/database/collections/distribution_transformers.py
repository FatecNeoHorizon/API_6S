from pymongo import ASCENDING,GEOSPHERE

def setup_distribution_transformers(db):
    db.create_collection(
        "distribution_transformers",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["code", "distributor_code", "geometry"],
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
                    "geodatabase_id": {
                        "bsonType": "objectId",
                        "description": "Reference to the geodatabases collection."
                    },
                    "connection_phases": {
                        "bsonType": ["string", "null"],
                        "enum": ["A", "B", "C", "AB", "AC", "BC", "ABC", "ABCN", None],
                        "description": "Connected phases. Mapped from FAS_CON."
                    },
                    "status": {
                        "bsonType": ["string", "null"],
                        "description": "Operational status. Mapped from SIT_ATIV."
                    },
                    "unit_type": {
                        "bsonType": ["string", "null"],
                        "description": "Unit type code. Mapped from TIP_UNID."
                    },
                    "position": {
                        "bsonType": ["string", "null"],
                        "description": "Position code. Mapped from POS."
                    },
                    "location_area": {
                        "bsonType": ["string", "null"],
                        "enum": ["1", "2", None],
                        "description": "Location area: 1 = Urban, 2 = Rural. Mapped from ARE_LOC."
                    },
                    "configuration": {
                        "bsonType": ["string", "null"],
                        "description": "Transformer configuration code. Mapped from CONF."
                    },
                    "substation": {
                        "bsonType": ["string", "null"],
                        "description": "Associated substation (posto). Mapped from POSTO."
                    },
                    "nominal_power_kva": {
                        "bsonType": ["double", "null"],
                        "description": "Nominal power in kVA. Mapped from POT_NOM."
                    },
                    "fuse_capacity": {
                        "bsonType": ["double", "null"],
                        "description": "Fuse capacity. Mapped from CAP_ELO."
                    },
                    "switch_capacity": {
                        "bsonType": ["double", "null"],
                        "description": "Switch capacity. Mapped from CAP_CHA."
                    },
                    "iron_losses_kw": {
                        "bsonType": ["double", "null"],
                        "description": "Iron (no-load) losses in kW. Mapped from PER_FER."
                    },
                    "copper_losses_kw": {
                        "bsonType": ["double", "null"],
                        "description": "Copper (load) losses in kW. Mapped from PER_COB."
                    },
                    "connection_date": {
                        "bsonType": ["string", "null"],
                        "description": "Connection date. Mapped from DAT_CON."
                    },
                    "geometry": {
                        "bsonType": "object",
                        "required": ["type", "coordinates"],
                        "description": "Transformer location in GeoJSON Point format.",
                        "properties": {
                            "type": {"bsonType": "string", "enum": ["Point"]},
                            "coordinates": {
                                "bsonType": "array",
                                "minItems": 2,
                                "maxItems": 2,
                                "items": {"bsonType": "double"}
                            }
                        }
                    }
                }
            }
        },
        validationLevel="moderate",
        validationAction="error"
    )

    col = db["distribution_transformers"]
    col.create_index([("geometry", GEOSPHERE)], name="idx_geo")
    col.create_index([("code", ASCENDING)], unique=True, name="idx_unique_code")
    col.create_index([("distributor_code", ASCENDING)], name="idx_distributor")
    col.create_index([("geodatabase_id", ASCENDING)], name="idx_geodatabase")
    col.create_index([("location_area", ASCENDING)], name="idx_location_area")
    col.create_index([("nominal_power_kva", ASCENDING)], name="idx_power")