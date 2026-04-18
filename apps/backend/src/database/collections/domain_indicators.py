from pymongo import ASCENDING

def setup_domain_indicators(db):
    db.create_collection(
        "domain_indicators",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["_id", "description", "group", "generation_date"],
                "properties": {
                    "_id": {
                        "bsonType": "string",
                        "description": "Indicator abbreviation (e.g., 'DEC', 'FEC'). Natural key. Mapped from SigIndicador."
                    },
                    "description": {
                        "bsonType": "string",
                        "description": "Full description of the indicator as published by ANEEL. Mapped from DscIndicador."
                    },
                    "group": {
                        "bsonType": "string",
                        "enum": ["continuity",
                                    "voltage_quality",
                                    "dimensioning",
                                    "compensations",
                                    "market"
                                ],
                        "description": "Thematic group of the indicator in the context of the Tecsys project."
                    },
                    "generation_date": {
                        "bsonType": "string",
                        "description": "Dataset generation date by ANEEL (YYYY-MM-DD). Mapped from DatGeracaoConjuntoDados."
                    }
                }
            }
        },
        validationLevel="strict",
        validationAction="error"
    )
    col = db["domain_indicators"]
    col.create_index([("indicator_id", ASCENDING)], unique=True)