from pymongo import ASCENDING


COLLECTION_NAME = "domain_indicators"

_VALIDATOR = {
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
                "enum": [
                    "continuity",
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
}


def create(db):
    if COLLECTION_NAME in db.list_collection_names():
        return

    db.create_collection(
        COLLECTION_NAME,
        validator=_VALIDATOR,
        validationLevel="strict",
        validationAction="error"
    )

    # Sem índices extras — _id é a sigla (chave natural), lookup O(1) nativo