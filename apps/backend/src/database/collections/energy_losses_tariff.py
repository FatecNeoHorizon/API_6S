from pymongo import ASCENDING

def setup_energy_losses_tariff(db, collections_exist):
    if "energy_losses_tariff" not in collections_exist:
        db.create_collection(
            "energy_losses_tariff",
            validator={
                "$jsonSchema":{
                    "bsonType": "object",
                    "required": [
                        "distributor",
                        "state",
                        "uf",
                        "process_date",
                        "tme_brl_mwh",
                        "basic_network_loss_mwh",
                        "technical_loss_mwh",
                        "non_technical_loss_mwh",
                        "basic_network_loss_cost_brl",
                        "technical_loss_cost_brl",
                        "non_technical_loss_cost_brl",
                        "parcel_b_brl",
                        "required_revenue_brl",
                        "distributor_slug"
                    ],
                    "properties": {
                        "_id":{
                            "bsonType": "objectId"
                        },
                        "distributor": {
                            "bsonType": "string",
                            "description": "Name of the energy distributor. Mapped from 'Distribuidora'."
                        },
                        "distributor_slug": {
                            "bsonType": "string",
                            "description": "Distributor identifier slug for joining with other collections. Mapped from 'sigla'."
                        },
                       "state": {
                           "bsonType": "string",
                            "description": "Full state name (ex: 'Amazonas'). Mapped from 'Estado'."
                        },
                        "uf": {
                            "bsonType": "string",
                            "description": "State abbreviation (ex: 'AM', 'SC'). Mapped from 'UF'."
                        },
                        "process_date": {
                            "bsonType": "string",
                            "description": "Tariff process reference date (YYYY-MM-DD). Mapped from 'Data do Processo'."
                        },
                        # --- Tarifa média de energia ---
                        "tme_brl_mwh": {
                            "bsonType": "double",
                            "description": "Average energy tariff in BRL/MWh at the time of the process. Mapped from 'TME (R$/MWh)'."
                        },
                        # --- Perdas em MWh ---
                        "basic_network_loss_mwh": {
                            "bsonType": "double",
                            "description": "Energy losses in the basic network (high voltage - AT) in MWh. Mapped from 'Perdas na Rede Básica (MWh)'."
                        },
                        "technical_loss_mwh": {
                            "bsonType": "double",
                            "description": "Technical energy losses (predominantly MT/AT) in MWh. Mapped from 'Perdas Técnicas (MWh)'."
                        },
                        "non_technical_loss_mwh": {
                            "bsonType": "double",
                            "description": "Non-technical losses — theft and fraud (MT/AT) in MWh. Mapped from 'Perdas Não Técnicas (MWh)'."
                        },
                        # --- Custos das perdas em R$ ---
                        "basic_network_loss_cost_brl": {
                            "bsonType": "double",
                            "description": "Financial cost of basic network losses in BRL. Mapped from 'Custo Perdas na Rede Básica (R$)'."
                        },
                        "technical_loss_cost_brl": {
                            "bsonType": "double",
                            "description": "Financial cost of technical losses in BRL. Mapped from 'Custo Perdas Técnicas (R$)'."
                        },
                        "non_technical_loss_cost_brl": {
                            "bsonType": "double",
                            "description": "Financial cost of non-technical losses (theft/fraud) in BRL. Mapped from 'Custo Perdas Não Técnicas (R$)'."
                        },
        
                        # --- Impacto regulatório ---
                        "parcel_b_brl": {
                            "bsonType": "double",
                            "description": "Parcel B of the tariff process in BRL — regulatory cost component. Mapped from 'Parcela B (R$)'."
                        },
                        "required_revenue_brl": {
                            "bsonType": "double",
                            "description": "Required revenue of the distributor in the tariff process in BRL. Mapped from 'Receita Requerida (R$)'."
                        }
                    }
                }
            },
            validationLevel="strict",
            validationAction="error"
        )

        col = db["energy_losses_tariff"]

        # Índice de unicidade — um registro por distribuidora por processo tarifário
        col.create_index(
            [("distributor_slug", ASCENDING),
             ("process_date", ASCENDING)],
            name="idx_unique_distributor_process",
            unique=True
        )

        # Índice por UF e data — análise geográfica por estado ao longo dos processos
        col.create_index(
            [("uf", ASCENDING),
             ("process_date", ASCENDING)],
            name="idx_uf_process_date"
        )

        # Índice por custo de perda não técnica — ranking de furto/fraude por distribuidora
        col.create_index(
            [("non_technical_loss_cost_brl", ASCENDING)],
            name="idx_non_technical_loss_cost"
        )
