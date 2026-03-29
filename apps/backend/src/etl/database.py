from pymongo import MongoClient, ASCENDING, GEOSPHERE

import os 
from dotenv import load_dotenv

load_dotenv()

def get_client():
    host = os.getenv("MONGO_HOST", "localhost")
    port = os.getenv("MONGO_PORT", "27017")
    user = os.getenv("MONGO_USER")
    password = os.getenv("MONGO_PASSWORD")
    db_name = os.getenv("MONGO_DB_NAME")
    mongo_uri = f"mongodb://{user}:{password}@mongo_db:{port}/{db_name}?authSource=admin"
    return MongoClient(mongo_uri)

def setup():
    mongo_db = os.getenv("MONGO_DB_NAME")
    client = get_client()
    db = client[mongo_db]

    collections_exist = db.list_collection_names()

    # ===========================================================================
    # COLLECTION: indicadores_dominio
    #
    # Tabela de referência com os 164 indicadores filtrados do domínio ANEEL.
    # _id = sigla do indicador (chave natural) — lookup O(1) sem índice extra.
    # ===========================================================================
    # ---------------------------------------------------------------------------
    # Grupos temáticos
    # ---------------------------------------------------------------------------
    # continuity      → DEC, FEC e variantes, NumOcorr, Nie, Pnie, NDIACRI
    # voltage_quality → DRP, DRC, ICC, TNS, DICVLD, DMICVLD, FICVLD e variantes
    # dimensioning    → ERP, PNIT, AREA, NumCon, NUCTCO e variantes
    # compensations   → COMPCONF, COMPCONT, PGUC*, PGUG*, QTUC*, QTUG*
    # market          → CMMT, CMMTCO, CMMTIN, CMMTRE, CMMTRU e variantes

    if "domain_indicators" not in collections_exist:
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

    # ===========================================================================
    # COLLECTION: distribution_indices
    #
    # Dados operacionais de qualidade e continuidade por conjunto de UCs.
    # Um documento por medição: indicador + distribuidora + conjunto + ano + período.
    # ===========================================================================
    # ---------------------------------------------------------------------------
    # Exemplo de documento
    # ---------------------------------------------------------------------------
    # {
    #     "_id":                           ObjectId("..."),
    #     "agent_acronym":                 "ENEL SP",
    #     "cnpj_number":                   "00.000.000/0001-00",
    #     "consumer_unit_set_id":          "SP-001",
    #     "consumer_unit_set_description": "Conjunto Centro SP",
    #     "indicator_type_code":           "DEC",
    #     "year":                          2023,
    #     "period":                        3,
    #     "value":                         4.72,
    #     "generation_date":               "2026-03-05"
    # }
    
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
                        "value",
                        "generation_date"
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
                        },
                        "generation_date": {
                            "bsonType": "string",
                            "description": "Data set generation date by ANEEL (YYYY-MM-DD). Mapped from DatGeracaoConjuntoDados."
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

    # ===========================================================================
    # COLLECTION: energy_losses_tariff
    #
    # Dados de perdas de energia por distribuidora e processo tarifário.
    # Granularidade: distribuidora / data do processo tarifário.
    # Cobre perdas na rede básica (AT), perdas técnicas e não técnicas (MT/AT)
    # com seus respectivos custos regulatórios em R$.
    #
    # Chave de join com outras collections: sigla ↔ sig_agente / distribuidora
    # ===========================================================================
    # ---------------------------------------------------------------------------
    # Mapeamento CSV → MongoDB
    # ---------------------------------------------------------------------------
    # Distribuidora               → distributor
    # Estado                      → state
    # UF                          → uf
    # Data do Processo            → process_date      (datetime → string YYYY-MM-DD)
    # TME (R$/MWh)                → tme_brl_mwh
    # Perdas na Rede Básica (MWh) → basic_network_loss_mwh
    # Perdas Técnicas (MWh)       → technical_loss_mwh
    # Perdas Não Técnicas (MWh)   → non_technical_loss_mwh
    # Custo Perdas na Rede Básica → basic_network_loss_cost_brl
    # Custo Perdas Técnicas (R$)  → technical_loss_cost_brl
    # Custo Perdas Não Técnicas   → non_technical_loss_cost_brl
    # Parcela B (R$)              → parcel_b_brl
    # Receita Requerida (R$)      → required_revenue_brl
    # sigla                       → distributor_slug
    
    # ---------------------------------------------------------------------------
    # Exemplo de documento
    # ---------------------------------------------------------------------------
    # {
    #     "_id":                        ObjectId("..."),
    #     "distributor":                "Amazonas Energia",
    #     "distributor_slug":           "Amazonas Energia",
    #     "state":                      "Amazonas",
    #     "uf":                         "AM",
    #     "process_date":               "2023-11-01",
    #     "tme_brl_mwh":                195.17,
    #     "basic_network_loss_mwh":     95581.132,
    #     "technical_loss_mwh":         786836.937,
    #     "non_technical_loss_mwh":     3269260.0,
    #     "basic_network_loss_cost_brl": 18655010.0,
    #     "technical_loss_cost_brl":    153570600.0,
    #     "non_technical_loss_cost_brl": 638076500.0,
    #     "parcel_b_brl":               386332500.0,
    #     "required_revenue_brl":       2847472000.0
    # }

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

    # ===========================================================================
    # COLLECTION: consumer_units_pj
    #
    # Flexible schema with subdocuments for demand and energy.
    # The voltage_level field ("AT" | "MT") is the main discriminator.
    #
    # Required fields: present in both AT and MT.
    # AT-only optional fields: at_transformer_code, demand.peak, demand.off_peak,
    #                          energy.peak, energy.off_peak
    # MT-only optional fields: mt_segment_code, at_transformer_unit, no_network,
    #                          base_date, demand.total, energy.total
    # ===========================================================================
    if "consumer_units_pj" not in collections_exist:
        db.create_collection(
            "consumer_units_pj",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "encrypted_id",
                        "voltage_level",
                        "distributor_code",
                        "service_point",
                        "substation",
                        "uc_set",
                        "municipality_code",
                        "sub_class",
                        "cnae",
                        "voltage_group",
                        "supply_voltage_kv",
                        "tariff_group",
                        "status",
                        "connection_date",
                        "system_type",
                        "contracted_demand_kw",
                        "location",
                        "dic",
                        "fic",
                    ],
                    "properties": {
                        "_id": {
                            "bsonType": "objectId"
                        },
                        "encrypted_id": {
                            "bsonType": "string",
                            "description": "Encrypted hash identifier of the consumer unit. Mapped from COD_ID_ENCR."
                        },
                        "voltage_level": {
                            "bsonType": "string",
                            "enum": ["AT", "MT"],
                            "description": "Voltage level discriminator. AT = High Voltage, MT = Medium Voltage."
                        },
                        "connection_point_number": {
                            "bsonType": ["string", "null"],
                            "description": "Number of the connection point. Mapped from 'NumPontoConexao'."
                        },
                        "distributor_code": {
                            "bsonType": "int",
                            "description": "Code of the distributor responsible for the consumer unit. Mapped from 'CodAgente'."
                        },
                        "service_point": {
                            "bsonType": "string",
                            "description": "Customer service point. Mapped from PAC."
                        },

                        # --- AT-only fields ---
                        "at_transformer_code": {
                            "bsonType": ["int", "null"],
                            "description": "[AT only] High voltage transformer code. Mapped from CTAT."
                        },
                        
                        # --- MT-only fields ---
                        "mt_segment_code": {
                            "bsonType": ["string", "null"],
                            "description": "[MT only] Medium voltage segment code. Mapped from CTMT."
                        },
                        "at_transformer_unit": {
                            "bsonType": ["string", "null"],
                            "description": "[MT only] AT transformer unit feeding the segment. Mapped from UNI_TR_AT."
                        },
                        "no_network": {
                            "bsonType": ["string", "null"],
                            "description": "[MT only] Indicates if the UC is off-grid (isolated). Mapped from SEMRED."
                        },
                        "base_date": {
                            "bsonType": ["string", "null"],
                            "description": "[MT only] Database reference date. Mapped from DATA_BASE."
                        },

                        # --- Network location ---
                        "substation": {
                            "bsonType": "string",
                            "description": "Substation code. Mapped from SUB."
                        },
                        "uc_set": {
                            "bsonType": "int",
                            "description": "Consumer unit set identifier. Join key with indices_distribuicao. Mapped from CONJ."
                        },
                        "municipality_code": {
                            "bsonType": "int",
                            "description": "IBGE municipality code. Mapped from MUN."
                        },

                        # --- Address ---
                        "street": {
                            "bsonType": ["string", "null"],
                            "description": "Street address of the UC. Mapped from LGRD."
                        },
                        "neighborhood": {
                            "bsonType": ["string", "null"],
                            "description": "Neighborhood of the UC. Mapped from BRR."
                        },
                        "zip_code": {
                            "bsonType": ["string", "null"],
                            "description": "ZIP code of the UC. Mapped from CEP."
                        },

                        # --- Classification ---
                        "sub_class": {
                            "bsonType": "string",
                            "description": "UC class and subclass (ex: 'SP2', 'IN'). Mapped from CLAS_SUB."
                        },
                        "cnae": {
                            "bsonType": "string",
                            "description": "CNAE economic activity code of the legal entity. Mapped from CNAE."
                        },
                        "connection_contract_type": {
                            "bsonType": ["string", "null"],
                            "description": "Connection and contract type (ex: 'A2-Tipo1'). Mapped from TIP_CC."
                        },
                        "connection_phases": {
                            "bsonType": ["string", "null"],
                            "description": "Connection phases (ex: 'ABC', 'ABCN'). Mapped from FAS_CON."
                        },
                        "voltage_group": {
                            "bsonType": "string",
                            "description": "Voltage group (ex: 'AT', 'MT'). Mapped from GRU_TEN."
                        },
                        "supply_voltage_kv": {
                            "bsonType": ["int", "null"],
                            "description": "Supply voltage in kV. Mapped from TEN_FORN."
                        },
                        "tariff_group": {
                            "bsonType": "string",
                            "description": "Tariff group (ex: 'A2', 'A3'). Mapped from GRU_TAR."
                        },
                        "status": {
                            "bsonType": "string",
                            "enum": ["AT", "DS"],
                            "description": "UC status: AT = Active, DS = Disconnected. Mapped from SIT_ATIV."
                        },
                        "connection_date": {
                            "bsonType": ["string", "null"],
                            "description": "UC connection date (DD/MM/YYYY). Mapped from DAT_CON."
                        },
                        "installed_load_kw": {
                            "bsonType": ["double", "null"],
                            "description": "Installed load in kW. Mapped from CAR_INST."
                        },
                        "free_market": {
                            "bsonType": ["int", "null"],
                            "description": "Free energy market choice indicator. Mapped from LIV."
                        },
                        "location_area": {
                            "bsonType": ["string", "null"],
                            "description": "Location area: UB = Urban, NU = Non-Urban. Mapped from ARE_LOC."
                        },
                        "system_type": {
                            "bsonType": "string",
                            "description": "System type: RD_INTERLIG = Interconnected Grid. Mapped from TIP_SIST."
                        },
                        "distributed_generation_code": {
                            "bsonType": ["string", "null"],
                            "description": "Distributed generation code, if applicable. Mapped from CEG_GD."
                        },
                        "contracted_demand_kw": {
                            "bsonType": "int",
                            "description": "Contracted demand in kW. Mapped from DEM_CONT."
                        },

                        # --- Monthly demand (flexible subdocument) ---
                        # AT: { peak: [12 values], off_peak: [12 values] }
                        # MT: { total: [12 values] }
                        "demand":{
                            "bsonType": "object",
                            "description": "Monthly demand in kW. AT: peak + off_peak. MT: total.",
                            "properties":{
                                "peak":{
                                    "bsonType": ["array", "null"],
                                    "description": "[AT only] Peak demand — 12 monthly values (kW). Mapped from DEM_P_01 to DEM_P_12.",
                                    "items":{"bsonType": ["double", "int", "null"]}
                                },
                                "off_peak":{
                                    "bsonType": ["array", "null"],
                                    "description": "[AT only] Off-peak demand — 12 monthly values (kW). Mapped from DEM_F_01 to DEM_F_12.",
                                    "items":{"bsonType": ["double", "int", "null"]
                                    }
                                },
                                "total":{
                                    "bsonType": ["array", "null"],
                                    "description": "[MT only] Total demand — 12 monthly values (kW). Mapped from DEM_01 to DEM_12.",
                                    "items":{"bsonType": ["double", "int", "null"]}
                                }
                            }
                        },
                        
                        # --- Monthly energy (flexible subdocument) ---
                        # AT: { peak: [12 values], off_peak: [12 values] }
                        # MT: { total: [12 values] }
                        "energy": {
                            "bsonType": "object",
                            "properties": {
                                "peak": {
                                    "bsonType": ["array", "null"],
                                    "items": {"bsonType": ["double", "int", "null"]}
                                },
                                "off_peak": {
                                    "bsonType": ["array", "null"],
                                    "items": {"bsonType": ["double", "int", "null"]}
                                },
                                "total": {
                                    "bsonType": ["array", "null"],
                                    "items": {"bsonType": ["double", "int", "null"]}
                                }
                            }
                        },

                        # --- Monthly DIC (12 values) ---
                        "dic":{
                            "bsonType": ["array", "null"],
                            "description": "Individual Interruption Duration per UC — 12 monthly values (minutes). Mapped from DIC_01 to DIC_12.",
                            "minItems": 12,
                            "maxItems": 12,
                            "items":{"bsonType": ["double", "int", "null"]}
                        },

                        # --- Monthly FIC (12 values) ---
                        "fic": {
                            "bsonType": "array",
                            "description": "Individual Interruption Frequency per UC — 12 monthly values. Mapped from FIC_01 to FIC_12.",
                            "minItems": 12,
                            "maxItems": 12,
                            "items": { "bsonType": ["double", "int", "null"] }
                        },

                        # --- Geolocation (GeoJSON for spatial queries) ---
                        "location": {
                            "bsonType": "object",
                            "required": ["type", "coordinates"],
                            "description": "Geographic coordinates in GeoJSON Point format.",
                            "properties": {
                                "type": {
                                    "bsonType": "string",
                                    "enum": ["Point"]
                                },
                                "coordinates": {
                                    "bsonType": "array",
                                    "description": "[longitude, latitude] — GeoJSON order. Mapped from POINT_X, POINT_Y.",
                                    "minItems": 2,
                                    "maxItems": 2,
                                    "items": { "bsonType": "double" }
                                }
                            }
                        },
        
                        "description": {
                            "bsonType": ["string", "null"],
                            "description": "Additional UC description. Mapped from DESCR."
                        }
                    }

                }
            },
            validationLevel="strict",
            validationAction="error"
        )

        col = db["consumer_units_pj"]

        # Geospatial index — base for heat map and regional spatial queries
        col.create_index(
            [("location", GEOSPHERE)],
            name="idx_geo"
        )

        # Uniqueness index — encrypted hash uniquely identifies each UC
        col.create_index(
            [("encrypted_id", ASCENDING)],
            name="idx_unique_encrypted_id",
            unique=True
        )

        # Composite analytical index — most common filters: distributor + voltage level + status
        col.create_index(
            [("distributor_code", ASCENDING),
             ("voltage_level", ASCENDING),
             ("status", ASCENDING)],
            name="idx_distributor_voltage_status"
        )

        # UC set index — join with distribution_indicators via uc_set field
        col.create_index(
            [("uc_set", ASCENDING),
            ("voltage_level", ASCENDING)],
            name="idx_uc_set_voltage"
        ) 

        # Municipality index — geographic analysis without coordinates
        col.create_index(
            [("municipality_code", ASCENDING)],
            name="idx_municipality"
        )

        # CNAE index — analysis by economic sector
        col.create_index(
            [("cnae", ASCENDING)],
            name="idx_cnae"
        )

    return db

if __name__ == "__main__":
    setup()