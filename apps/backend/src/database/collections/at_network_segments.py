from pymong import ASCENDING, GEOSPHERE

def setup_at_network_segments(db, collections_exist):
    if "at_network_segments" not in collections_exist:
        db.create_collection(
            "at_network_segments",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "code",
                        "distributor_code",
                        "connection_phases",
                        "geometry",
                        "geodatabase_id"
                    ],
                    "properties": {
                        "_id": {"bsonType": "objectId"},
    
                        # --- Identification ---
                        "code": {
                            "bsonType": "string",
                            "description": "Unique segment identifier. Mapped from COD_ID."
                        },
                        "distributor_code": {
                            "bsonType": ["string", "null"],
                            "description": "Distributor code. Mapped from DIST."
                        },
                        "description": {
                            "bsonType": ["string", "null"],
                            "description": "Segment description. Mapped from DESCR."
                        },
                        "geodatabase_id": {
                            "bsonType": "objectId",
                            "description": "Reference to the geodatabases collection."
                        },
    
                        # --- Network references ---
                        "connection_point_start": {
                            "bsonType": ["string", "null"],
                            "description": "Start connection point. Mapped from PN_CON_1."
                        },
                        "connection_point_end": {
                            "bsonType": ["string", "null"],
                            "description": "End connection point. Mapped from PN_CON_2."
                        },
                        "feeder_code": {
                            "bsonType": ["string", "null"],
                            "description": "Feeder code. Mapped from ALIM."
                        },
                        "line_code": {
                            "bsonType": ["string", "null"],
                            "description": "Line code. Mapped from LI."
                        },
                        "capacitor_unit":    {"bsonType": ["string", "null"], "description": "Mapped from UNI_CAP."},
                        "regulator_unit":    {"bsonType": ["string", "null"], "description": "Mapped from UNI_REG."},
                        "sectionalizer_unit":{"bsonType": ["string", "null"], "description": "Mapped from UNI_SEC."},
    
                        # --- Electrical characteristics ---
                        "connection_phases": {
                            "bsonType": "string",
                            "enum": ["A", "B", "C", "AB", "AC", "BC", "ABC", "ABCN"],
                            "description": "Connected phases. Mapped from FAS_CON."
                        },
                        "cable_formation":    {"bsonType": ["string", "null"], "description": "Mapped from FORM_CAB."},
                        "position": {
                            "bsonType": ["string", "null"],
                            "enum": ["D", "O", None],
                            "description": "Position: D = Distribution, O = Other. Mapped from POS."
                        },
                        "voltage_level_code": {"bsonType": ["int", "null"],    "description": "Voltage level code (kV). Mapped from NIV."},
                        "geometry_cable_type":{"bsonType": ["string", "null"], "description": "Mapped from GEOM_CAB."},
                        "jumper":             {"bsonType": ["string", "null"], "description": "Mapped from JUM."},
    
                        # --- Phase conductor ---
                        "phase_conductor": {
                            "bsonType": "object",
                            "properties": {
                                "bit":         {"bsonType": ["string", "null"]},
                                "material":    {"bsonType": ["string", "null"]},
                                "insulation":  {"bsonType": ["string", "null"]},
                                "odi":         {"bsonType": ["string", "null"]},
                                "type":        {"bsonType": ["string", "null"]},
                                "ampacity":    {"bsonType": ["double", "null"]},
                                "tuc":         {"bsonType": ["string", "null"]},
                                "resistances": {"bsonType": ["array",  "null"], "items": {"bsonType": ["double", "null"]}},
                                "iduc":        {"bsonType": ["string", "null"]},
                                "uar":         {"bsonType": ["string", "null"]},
                            }
                        },
    
                        # --- Neutral conductor ---
                        "neutral_conductor": {
                            "bsonType": "object",
                            "properties": {
                                "bit":         {"bsonType": ["string", "null"]},
                                "material":    {"bsonType": ["string", "null"]},
                                "insulation":  {"bsonType": ["string", "null"]},
                                "odi":         {"bsonType": ["string", "null"]},
                                "type":        {"bsonType": ["string", "null"]},
                                "ampacity":    {"bsonType": ["double", "null"]},
                                "tuc":         {"bsonType": ["string", "null"]},
                                "resistances": {"bsonType": ["array",  "null"], "items": {"bsonType": ["double", "null"]}},
                                "iduc":        {"bsonType": ["string", "null"]},
                                "uar":         {"bsonType": ["string", "null"]},
                            }
                        },
    
                        # --- Physical ---
                        "length_m":    {"bsonType": ["double", "null"], "description": "Mapped from COMP."},
                        "shape_length":{"bsonType": ["double", "null"], "description": "Mapped from Shape_Length."},
    
                        # --- Geometry ---
                        "geometry": {
                            "bsonType": "object",
                            "required": ["type", "coordinates"],
                            "properties": {
                                "type": {"bsonType": "string", "enum": ["MultiLineString", "LineString"]}
                            }
                        }
                    }
                }
            },
            validationLevel="moderate",
            validationAction="error"
    )
    
        col = db["at_network_segments"]
        col.create_index([("geometry", GEOSPHERE)], name="idx_geo")
        col.create_index([("code", ASCENDING)], unique=True, name="idx_unique_code")
        col.create_index([("feeder_code", ASCENDING)], name="idx_feeder")
        col.create_index([("geodatabase_id", ASCENDING)], name="idx_geodatabase")
        col.create_index([("distributor_code", ASCENDING)], name="idx_distributor")
        col.create_index([("voltage_level_code", ASCENDING)], name="idx_voltage_level")
