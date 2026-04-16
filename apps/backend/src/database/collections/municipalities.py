from pymongo import ASCENDING, GEOSPHERE

def setup_municipalities(db, collections_exist):
    if "municipalities" not in collections_exist:
        db.create_collection(
            "municipalities",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["code", "ibge_code", "name", "geometry", "geodatabase_id"],
                    "properties": {
                        "_id": {"bsonType": "objectId"},
                        "code": {
                            "bsonType": "string",
                            "description": "Internal GDB identifier. Mapped from COD_ID."
                        },
                        "ibge_code": {
                            "bsonType": ["string", "null"],
                            "description": "IBGE municipality code. Mapped from IBGE_MUN."
                        },
                        "ibge_uf_code": {
                            "bsonType": ["string", "null"],
                            "description": "IBGE state code. Mapped from IBGE_UF."
                        },
                        "name": {
                            "bsonType": "string",
                            "description": "Municipality name. Mapped from NOM."
                        },
                        "description": {
                            "bsonType": ["string", "null"],
                            "description": "Additional description. Mapped from DESCR."
                        },
                        "management_area": {
                            "bsonType": ["string", "null"],
                            "description": "Distributor management area. Mapped from GERENCIA."
                        },
                        "distributor_code": {
                            "bsonType": ["string", "null"],
                            "description": "Distributor code. Mapped from DIST."
                        },
                        "shape_length": {
                            "bsonType": ["double", "null"],
                            "description": "Perimeter length. Mapped from Shape_Length."
                        },
                        "shape_area": {
                            "bsonType": ["double", "null"],
                            "description": "Area in map units. Mapped from Shape_Area."
                        },
                        "geodatabase_id": {
                            "bsonType": "objectId",
                            "description": "Reference to the geodatabases collection."
                        },
                        "geometry": {
                            "bsonType": "object",
                            "required": ["type", "coordinates"],
                            "properties": {
                                "type": {"bsonType": "string", "enum": ["MultiPolygon", "Polygon"]}
                            }
                        }
                    }
                }
            },
            validationLevel="strict",
            validationAction="error"
        )
        
        col = db["municipalities"]
        col.create_index([("geometry", GEOSPHERE)], name="idx_geo")
        col.create_index([("code", ASCENDING)], unique=True, name="idx_unique_code")
        col.create_index([("ibge_code", ASCENDING)], name="idx_ibge")
        col.create_index([("geodatabase_id", ASCENDING)], name="idx_geodatabase")