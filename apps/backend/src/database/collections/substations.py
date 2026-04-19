from pymongo import ASCENDING, GEOSPHERE

def setup_substations(db):
    db.create_collection(
        "substations",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["code", "distributor_code", "geometry", "geodatabase_id"],
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

    col = db["substations"]
    col.create_index([("geometry", GEOSPHERE)], name="idx_geo")
    col.create_index([("code", ASCENDING)], unique=True, name="idx_unique_code")
    col.create_index([("distributor_code", ASCENDING)], name="idx_distributor")
    col.create_index([("geodatabase_id", ASCENDING)], name="idx_geodatabase")