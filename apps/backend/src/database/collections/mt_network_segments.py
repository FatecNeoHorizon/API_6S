from pymongo import ASCENDING, GEOSPHERE

def setup_mt_network_segments(db, collections_exist):
    if "mt_network_segments" not in collections_exist:
        db.create_collection(
            "mt_network_segments",
            validator={
                "$jsonSchema":{
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
                            "description": "Reference to the geodatabases collection — which GDB import this came from."
                        },

                        # --- Network references ---
                        "connection_point_start":{
                            "bsonType": ["string", "null"],
                            "description": "Start connection point of the segment. Mapped from PN_CON_1."
                        },
                        "connection_point_end": {
                            "bsonType": ["string", "null"],
                            "description": "End connection point of the segment. Mapped from PN_CON_2."
                        },
                        "feeder_code": {
                            "bsonType": ["string", "null"],
                            "description": "Feeder (alimentador) code this segment belongs to. Mapped from ALIM."
                        },
                        "line_code": {
                            "bsonType": ["string", "null"],
                            "description": "Line code. Mapped from LI."
                        },
                        "capacitor_unit": {
                            "bsonType": ["string", "null"],
                            "description": "Associated capacitor unit. Mapped from UNI_CAP."
                        },
                        "regulator_unit": {
                            "bsonType": ["string", "null"],
                            "description": "Associated voltage regulator unit. Mapped from UNI_REG."
                        },
                        "sectionalizer_unit": {
                            "bsonType": ["string", "null"],
                            "description": "Associated sectionalizer unit. Mapped from UNI_SEC."
                        },
                        "transformer_unit": {
                            "bsonType": ["string", "null"],
                            "description": "[MT only] Distribution transformer unit feeding this segment. Mapped from UNI_TR_D."
                        },

                        # --- Electrical characteristics ---
                        "connection_phases": {
                            "bsonType": "string",
                            "enum": ["A", "B", "C", "AB", "AC", "BC", "ABC", "ABCN"],
                            "description": "Connected phases. Mapped from FAS_CON."
                        },
                        "cable_formation": {
                            "bsonType": ["string", "null"],
                            "description": "Cable formation type code. Mapped from FORM_CAB."
                        },
                        "position": {
                            "bsonType": ["string", "null"],
                            "description": "Segment position: D = Distribution. Mapped from POS."
                        },
                        "voltage_level_code": {
                            "bsonType": ["int", "null"],
                            "description": "Voltage level code (kV). Mapped from NIV."
                        },
                        "geometry_cable_type": {
                            "bsonType": ["string", "null"],
                            "description": "Cable geometry type code. Mapped from GEOM_CAB."
                        },
                        "jumper": {
                            "bsonType": ["string", "null"],
                            "description": "Jumper indicator. Mapped from JUM."
                        },

                        # --- Phase conductor properties ---
                        "phase_conductor": {
                        "bsonType": "object",
                        "description": "Phase conductor technical properties.",
                        "properties": {
                            "bit":          {"bsonType": ["string", "null"], "description": "Conductor section/gauge. Mapped from BIT_FAS."},
                            "material":     {"bsonType": ["string", "null"], "description": "Material code. Mapped from MAT_FAS."},
                            "insulation":   {"bsonType": ["string", "null"], "description": "Insulation type. Mapped from ISO_FAS."},
                            "odi":          {"bsonType": ["string", "null"], "description": "Odi code. Mapped from ODI_FAS."},
                            "type":         {"bsonType": ["string", "null"], "description": "Conductor type. Mapped from TI_FAS."},
                            "ampacity":     {"bsonType": ["double", "null"], "description": "Current carrying capacity (A). Mapped from CM_FAS."},
                            "tuc":          {"bsonType": ["string", "null"], "description": "TUC code. Mapped from TUC_FAS."},
                            "resistances":  {
                                "bsonType": ["array", "null"],
                                "description": "Resistance values A1-A6. Mapped from A1_FAS to A6_FAS.",
                                "items": {"bsonType": ["double", "null"]}
                            },
                            "iduc":         {"bsonType": ["string", "null"], "description": "IDUC code. Mapped from IDUC_FAS."},
                            "uar":          {"bsonType": ["string", "null"], "description": "UAR code. Mapped from UAR_FAS."},
                            }
                        },
                        
                        # --- Neutral conductor properties ---
                        "neutral_conductor": {
                            "bsonType": "object",
                            "description": "Neutral conductor technical properties.",
                            "properties": {
                                "bit":          {"bsonType": ["string", "null"], "description": "Conductor section/gauge. Mapped from BIT_NEU."},
                                "material":     {"bsonType": ["string", "null"], "description": "Material code. Mapped from MAT_NEU."},
                                "insulation":   {"bsonType": ["string", "null"], "description": "Insulation type. Mapped from ISO_NEU."},
                                "odi":          {"bsonType": ["string", "null"], "description": "Odi code. Mapped from ODI_NEU."},
                                "type":         {"bsonType": ["string", "null"], "description": "Conductor type. Mapped from TI_NEU."},
                                "ampacity":     {"bsonType": ["double", "null"], "description": "Current carrying capacity (A). Mapped from CP_CM_NEU."},
                                "tuc":          {"bsonType": ["string", "null"], "description": "TUC code. Mapped from TUC_NEU."},
                                "resistances":  {
                                    "bsonType": ["array", "null"],
                                    "description": "Resistance values A1-A6. Mapped from A1_NEU to A6_NEU.",
                                    "items": {"bsonType": ["double", "null"]}
                                },
                                "iduc":         {"bsonType": ["string", "null"], "description": "IDUC code. Mapped from IDUC_NEU."},
                                "uar":          {"bsonType": ["string", "null"], "description": "UAR code. Mapped from UAR_NEU."},
                            }
                        },

                        # --- Physical properties ---
                        "length_m": {
                            "bsonType": ["double", "null"],
                            "description": "Segment length in meters. Mapped from COMP."
                        },
                        "shape_length": {
                            "bsonType": ["double", "null"],
                            "description": "Shape length from GDB. Mapped from Shape_Length."
                        },

                         # --- Geometry (GeoJSON MultiLineString) ---
                        "geometry": {
                            "bsonType": "object",
                            "required": ["type", "coordinates"],
                            "description": "Segment geometry in GeoJSON format.",
                            "properties": {
                                "type": {"bsonType": "string", "enum": ["MultiLineString", "LineString"]}
                            }
                        }
                    }
                } 
            },
            validationLevel="strict",
            validationAction="error"
        )

        col = db["mt_network_segments"]
        col.create_index([("geometry", GEOSPHERE)], name="idx_geo")
        col.create_index([("code", ASCENDING)], unique=True, name="idx_unique_code")
        col.create_index([("feeder_code", ASCENDING)], name="idx_feeder")
        col.create_index([("geodatabase_id", ASCENDING)], name="idx_geodatabase")
        col.create_index([("distributor_code", ASCENDING)], name="idx_distributor")
        col.create_index([("voltage_level_code", ASCENDING)], name="idx_voltage_level")