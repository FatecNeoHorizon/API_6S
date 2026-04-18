from pymongo import ASCENDING

def setup_distribution_indices(db, collections_exist):
    if "distribution_indices" not in collections_exist:
        db.create_collection(
            "distribution_indices",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "agent_acronym",
                        "cnpj_number",
                        "consumer_unit_set_id",
                        "consumer_unit_set_description",
                        "indicator_type_code",
                        "year",
                        "period",
                        "value"
                    ],
                    "properties": {
                        "_id":{
                            "bsonType": "objectId"
                        },
                        "agent_acronym": {
                            "bsonType": "string",
                            "description": "Distributor acronym (e.g., 'ENEL SP'). Mapped from SigAgente."
                        },
                        "cnpj_number": {
                            "bsonType": "string",
                            "description": "Distributor's CNPJ. Mapped from NumCNPJ."
                        },
                        "consumer_unit_set_id": {
                            "bsonType": "string",
                            "description": "Identifier of the set of Consumer Units. Mapped from IdeConjUndConsumidoras."
                        },
                        "consumer_unit_set_description": {
                            "bsonType": "string",
                            "description": "Description of the set of Consumer Units. Mapped from DscConjUndConsumidoras."
                        },
                        "indicator_type_code": {
                            "bsonType": "string",
                            "description": "Indicator acronym. Reference to indicators_domain._id. Mapped from SigIndicador."
                        },
                        "year": {
                            "bsonType": "int",
                            "description": "Year of the measurement. Mapped from Ano."
                        },
                        "period": {
                            "bsonType": "int",
                            "minimum": 1,
                            "maximum": 12,
                            "description": "Index period/month (1–12). Mapped from IndexPeriodNumber."
                        },
                        "value": {
                            "bsonType": ["double", "null"],
                            "description": "Value of the index sent by the distributor. Null if invalid. Mapped from VlrIndiceEnviado."
                        }
                    }
                }
            },
            validationLevel="strict",
            validationAction="error"
        )
        
        col = db["distribution_indices"]

        # Índice composto principal — cobre a maioria das queries analíticas
        col.create_index([("indicator_type_code", ASCENDING),
                          ("year", ASCENDING),
                          ("agent_acronym", ASCENDING)],
                         name="idx_indicator_year_agent"
                        )

        # Índice por conjunto — join com unidades_consumidoras_pj via conj
        col.create_index(
            [("consumer_unit_set_id", ASCENDING),
             ("indicator_type_code", ASCENDING),
             ("year", ASCENDING)],
            name="idx_set_indicator_year"
        )

        # Índice por CNPJ — lookup por distribuidora
        col.create_index(
            [("cnpj_number", ASCENDING)],
            name="idx_cnpj"
        )

        # Índice de unicidade — idempotência no ETL via upsert
        col.create_index(
            [("agent_acronym", ASCENDING),
             ("consumer_unit_set_id", ASCENDING),
             ("indicator_type_code", ASCENDING),
             ("year", ASCENDING),
             ("period", ASCENDING)],
            name="idx_unique_measurement",
            unique=True
        )