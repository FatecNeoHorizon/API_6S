from pymongo import MongoClient, GEOSPHERE

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME   = "zeus"

def get_client():
    return MongoClient(MONGO_URI)

def setup():
    client = get_client()

    client.list_database_names()

    if DB_NAME not in client.list_database_names(): 
        db = client[DB_NAME]

    collections_exist = db.list_collection_names()

    if "arat" not in collections_exist:
        db.create_collection("arat", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["code","name", "geometry"],
                "properties": {
                    "name":      {"bsonType": "string"},
                    "code":      {"bsonType": "string"},
                    "status":    {"enum": ["active", "inactive"]},
                    "shape_length":    {"bsonType": "double"},
                    "shape_area":      {"bsonType": "double"},
                    "geometry": {
                        "bsonType": "object",
                        "required": ["type", "coordinates"],
                        "properties": {
                            "type": {"enum": ["Polygon", "MultiPolygon"]}
                        }
                    },
                    "conj": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "properties": {
                                "name":       {"bsonType": "string"},
                                "code":       {"bsonType": "string"},
                            }
                        }
                    }
                }
            }
        })
        db.arat.create_index([("geometry", GEOSPHERE)])
        db.arat.create_index("code", unique=True, sparse=True)

    if "conj" not in collections_exist:
        db.create_collection("conj", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["name", "code", "geometry"],
                "properties": {
                    "name":    {"bsonType": "string"},
                    "code":  {"bsonType": "string"},
                    "status":  {"enum": ["active", "inactive"]},
                    "shape_length":    {"bsonType": "double"},
                    "shape_area":      {"bsonType": "double"},
                    "arat_id":         {"bsonType": "objectId"},
                    "geometry": {
                        "bsonType": "object",
                        "required": ["type", "coordinates"],
                        "properties": {
                            "type": {"enum": ["Polygon", "MultiPolygon"]}
                        }
                    },
                    "ucmt": {
                        "bsonType": "array",
                        "items": {
                            "bsonType": "object",
                            "properties": {
                                "name":   {"bsonType": "string"},
                                "code": {"bsonType": "string"}
                            }
                        }
                    }
                }
            }
        })
        db.conj.create_index([("geometry", GEOSPHERE)])
        db.conj.create_index("code", unique=True, sparse=True)

    if "ucmt" not in collections_exist:
        db.create_collection("ucmt", validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["nome", "codigo", "conj_id", "geometry"],
                "properties": {
                    "nome":   {"bsonType": "string"},
                    "codigo": {"bsonType": "string"},
                    "status": {"enum": ["ativo", "inativo"]},
                    "conj_id":       {"bsonType": "objectId"},
                    "geometry": {
                        "bsonType": "object",
                        "required": ["type", "coordinates"],
                        "properties": {
                            "type": {"enum": ["Polygon", "MultiPolygon", "Point"]}
                        }
                    },
                    "dic01":      {"bsonType": "double"},
                    "dic02":      {"bsonType": "double"},
                    "dic03":      {"bsonType": "double"},
                    "dic04":      {"bsonType": "double"},
                    "dic05":      {"bsonType": "double"},
                    "dic06":      {"bsonType": "double"},
                    "dic07":      {"bsonType": "double"},
                    "dic08":      {"bsonType": "double"},
                    "dic09":      {"bsonType": "double"},
                    "dic10":      {"bsonType": "double"},
                    "dic11":      {"bsonType": "double"},
                    "dic12":      {"bsonType": "double"},
                    "fic01":      {"bsonType": "double"},
                    "fic02":      {"bsonType": "double"},
                    "fic03":      {"bsonType": "double"},
                    "fic04":      {"bsonType": "double"},
                    "fic05":      {"bsonType": "double"},
                    "fic06":      {"bsonType": "double"},
                    "fic07":      {"bsonType": "double"},
                    "fic08":      {"bsonType": "double"},
                    "fic09":      {"bsonType": "double"},
                    "fic10":      {"bsonType": "double"},
                    "fic11":      {"bsonType": "double"},
                    "fic12":      {"bsonType": "double"}
                }
            }
        })
        db.ucmt.create_index([("geometry", GEOSPHERE)])
        db.ucmt.create_index("conj_id")
        db.ucmt.create_index("code", unique=True)

    if "logs_import" not in collections_exist:
        db.create_collection("logs_import",validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["user", "date_import", "file"],
                "properties": {
                    "user": {
                        "bsonType": "string",
                        "description": "User that imported the file"
                    },
                    "date_import": {
                        "bsonType": "date",
                        "description": "Date and time of the import"
                    },
                    "file": {
                        "bsonType": "string",
                        "description": "Name of the imported file"
                    },
                    "status": {
                        "bsonType": "string",
                        "enum": ["SUCCESS", "ERROR"],
                        "description": "Status of the import"
                    }
                }
            }
        })
        db.logs_import.create_index("date_import")
        db.logs_import.create_index("user")
    return db

if __name__ == "__main__":
    setup()