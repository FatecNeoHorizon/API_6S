from pymongo import ASCENDING, GEOSPHERE

def setup_consumer_units_pj(db):
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
                    "at_transformer_code": {
                        "bsonType": ["int", "null"],
                        "description": "[AT only] High voltage transformer code. Mapped from CTAT."
                    },
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
                    "dic":{
                        "bsonType": ["array", "null"],
                        "description": "Individual Interruption Duration per UC — 12 monthly values (minutes). Mapped from DIC_01 to DIC_12.",
                        "minItems": 12,
                        "maxItems": 12,
                        "items":{"bsonType": ["double", "int", "null"]}
                    },
                    "fic": {
                        "bsonType": "array",
                        "description": "Individual Interruption Frequency per UC — 12 monthly values. Mapped from FIC_01 to FIC_12.",
                        "minItems": 12,
                        "maxItems": 12,
                        "items": { "bsonType": ["double", "int", "null"] }
                    },
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

    col.create_index(
        [("location", GEOSPHERE)],
        name="idx_geo"
    )

    col.create_index(
        [("encrypted_id", ASCENDING)],
        name="idx_unique_encrypted_id",
        unique=True
    )

    col.create_index(
        [("distributor_code", ASCENDING),
            ("voltage_level", ASCENDING),
            ("status", ASCENDING)],
        name="idx_distributor_voltage_status"
    )
    col.create_index(
        [("uc_set", ASCENDING),
        ("voltage_level", ASCENDING)],
        name="idx_uc_set_voltage"
    ) 
    col.create_index(
        [("municipality_code", ASCENDING)],
        name="idx_municipality"
    )
    col.create_index(
        [("cnae", ASCENDING)],
        name="idx_cnae"
    )