from pymongo import ASCENDING, GEOSPHERE

"""
Example Document:
{
  "_id": "ObjectId('68f63cd3e9d041a73c2b646a')",
  "name": "São Francisco",
  "code": "12596",
  "status": "active",
  "shape_length": 142.5,
  "shape_area": 890.3,
  "arat_id": "ObjectId('68f63cd3e9d041a73c2b646b')",
  "geodatabase_id": "ObjectId('68f63cd3e9d041a73c2b646c')",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [[[ ... ]]]
  },
  "distribution_indices": [
    {
      "indicator_type_code": "DEC",
      "year": 2024,
      "period": 1,
      "value": 1.60
    }
  ],
  "annual_summaries": [
    {
      "indicator_type_code": "DEC",
      "year": 2024,
      "accumulated_value": 7.20,
      "periods_count": 6,
      "status": "partial",
      "limit": 8.00,
      "criticality": "normal"
    }
  ]
}
"""

def setup_conj(db):
    db.create_collection(
        "conj",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "code", "geodatabase_id", "geometry"],
                "properties": {
                    "_id": {"bsonType": "objectId"},
                    "name": {
                        "bsonType": "string",
                        "description": "UC set display name. Mapped from GDB DESCR."
                    },
                    "code": {
                        "bsonType": "string",
                        "description": "UC set identifier. Mapped from GDB COD_ID."
                    },
                    "status": {
                        "bsonType": ["string", "null"],
                        "enum": ["active", "inactive", None],
                        "description": "Active or inactive status."
                    },
                    "shape_length": {
                        "bsonType": ["double", "null"],
                        "description": "Perimeter of the UC set boundary in map units. Mapped from Shape_Length."
                    },
                    "shape_area": {
                        "bsonType": ["double", "null"],
                        "description": "Area of the UC set in map units. Mapped from Shape_Area."
                    },
                    "arat_id": {
                        "bsonType": ["objectId", "null"],
                        "description": "Reference to the distributor area polygon (arat collection)."
                    },
                    "geodatabase_id": {
                        "bsonType": "objectId",
                        "description": "Reference to geodatabases._id."
                    },
                    "geometry": {
                        "bsonType": "object",
                        "required": ["type", "coordinates"],
                        "properties": {
                            "type": {"bsonType": "string", "enum": ["MultiPolygon", "Polygon"]},
                            "coordinates": {"bsonType": "array"}
                        }
                    },
                    "distribution_indices": {
                        "bsonType": ["array", "null"],
                        "description": "Monthly measurements of indicators.",
                        "items": {
                            "bsonType": "object",
                            "required": ["indicator_type_code", "year", "period"],
                            "properties": {
                                "indicator_type_code": {"bsonType": "string"},
                                "year": {"bsonType": "int"},
                                "period": {"bsonType": "int", "minimum": 1, "maximum": 12},
                                "value": {"bsonType": ["double", "null"]}
                            }
                        }
                    },
                    "annual_summaries": {
                        "bsonType": ["array", "null"],
                        "description": "Annual summary by indicator.",
                        "items": {
                            "bsonType": "object",
                            "required": ["indicator_type_code", "year", "accumulated_value", "periods_count", "status"],
                            "properties": {
                                "indicator_type_code": {"bsonType": "string"},
                                "year": {"bsonType": "int"},
                                "accumulated_value": {"bsonType": ["double", "null"]},
                                "periods_count": {"bsonType": "int", "minimum": 1, "maximum": 12},
                                "status": {"bsonType": "string", "enum": ["complete", "partial"]},
                                "limit": {"bsonType": ["double", "null"]},
                                "criticality": {"bsonType": ["string", "null"], "enum": ["normal", "attention", "critical", None]}
                            }
                        }
                    }
                }
            }
        },
        validationLevel="strict",
        validationAction="error"
    )

    col = db["conj"]
    col.create_index([("geometry", GEOSPHERE)], name="idx_geo")
    col.create_index([("code", ASCENDING)], unique=True, name="idx_unique_code")
    col.create_index([("status", ASCENDING)], name="idx_status")
    col.create_index([("geodatabase_id", ASCENDING)], name="idx_geodatabase")
