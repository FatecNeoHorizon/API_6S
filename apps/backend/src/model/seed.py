from pymongo import MongoClient
from bson import ObjectId
import os
from src.etl.database import get_client

def seed():
    client = get_client()
    db = client[os.getenv("MONGO_DB_NAME")]

    count = db["substations"].count_documents({})
    print(f"🔍 Substações no banco: {count}")

    if count > 0:
        print("⏭️  Seed ignorado — banco já tem dados.")
        return

    gdb_id = ObjectId()

    se_centro = "SE-001"
    se_norte  = "SE-002"
    se_sul    = "SE-003"

    feeder_centro_1 = "ALIM-001"
    feeder_centro_2 = "ALIM-002"
    feeder_norte_1  = "ALIM-003"
    feeder_sul_1    = "ALIM-004"

    # ===========================================================================
    # MUNICIPALITIES
    # FIX: MultiPolygon correto — 4 níveis de array, não 5
    # [polygon][ring][point] → coordinates: [ [ [ [lon, lat], ... ] ] ]
    # ===========================================================================
    municipalities = [
        {
            "code": "MUN-001",
            "ibge_code": "3550308",
            "ibge_uf_code": "35",
            "name": "São Paulo - Centro",
            "description": "Região central",
            "management_area": "Centro",
            "distributor_code": "001",
            "geodatabase_id": gdb_id,
            "shape_length": 12000.0,
            "shape_area": 8000000.0,
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [-46.6500, -23.5600],
                            [-46.6200, -23.5600],
                            [-46.6200, -23.5300],
                            [-46.6500, -23.5300],
                            [-46.6500, -23.5600]
                        ]
                    ]
                ]
            }
        },
        {
            "code": "MUN-002",
            "ibge_code": "3534401",
            "ibge_uf_code": "35",
            "name": "São Paulo - Norte",
            "description": "Região norte",
            "management_area": "Norte",
            "distributor_code": "001",
            "geodatabase_id": gdb_id,
            "shape_length": 10000.0,
            "shape_area": 6000000.0,
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [-46.6600, -23.5200],
                            [-46.6300, -23.5200],
                            [-46.6300, -23.4900],
                            [-46.6600, -23.4900],
                            [-46.6600, -23.5200]
                        ]
                    ]
                ]
            }
        },
        {
            "code": "MUN-003",
            "ibge_code": "3548708",
            "ibge_uf_code": "35",
            "name": "São Paulo - Sul",
            "description": "Região sul",
            "management_area": "Sul",
            "distributor_code": "001",
            "geodatabase_id": gdb_id,
            "shape_length": 11000.0,
            "shape_area": 7000000.0,
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [-46.6500, -23.6200],
                            [-46.6200, -23.6200],
                            [-46.6200, -23.5900],
                            [-46.6500, -23.5900],
                            [-46.6500, -23.6200]
                        ]
                    ]
                ]
            }
        }
    ]

    # ===========================================================================
    # SUBSTATIONS
    # FIX: mesmo fix do MultiPolygon
    # ===========================================================================
    substations = [
        {
            "code": se_centro,
            "distributor_code": "001",
            "description": "Subestacao Centro",
            "geodatabase_id": gdb_id,
            "shape_length": 400.0,
            "shape_area": 10000.0,
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [-46.6360, -23.5510],
                            [-46.6340, -23.5510],
                            [-46.6340, -23.5490],
                            [-46.6360, -23.5490],
                            [-46.6360, -23.5510]
                        ]
                    ]
                ]
            }
        },
        {
            "code": se_norte,
            "distributor_code": "001",
            "description": "Subestacao Norte",
            "geodatabase_id": gdb_id,
            "shape_length": 380.0,
            "shape_area": 9000.0,
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [-46.6420, -23.5080],
                            [-46.6400, -23.5080],
                            [-46.6400, -23.5060],
                            [-46.6420, -23.5060],
                            [-46.6420, -23.5080]
                        ]
                    ]
                ]
            }
        },
        {
            "code": se_sul,
            "distributor_code": "001",
            "description": "Subestacao Sul",
            "geodatabase_id": gdb_id,
            "shape_length": 360.0,
            "shape_area": 8500.0,
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [-46.6380, -23.6080],
                            [-46.6360, -23.6080],
                            [-46.6360, -23.6060],
                            [-46.6380, -23.6060],
                            [-46.6380, -23.6080]
                        ]
                    ]
                ]
            }
        }
    ]

    # ===========================================================================
    # DISTRIBUTION TRANSFORMERS
    # ===========================================================================
    distribution_transformers = [
        {
            "code": "TR-001-A",
            "distributor_code": "001",
            "description": "Transformador Centro A",
            "geodatabase_id": gdb_id,
            "connection_phases": "ABC",
            "status": "SM",
            "unit_type": "51",
            "position": "D",
            "location_area": "1",
            "configuration": "RA",
            "substation": se_centro,
            "nominal_power_kva": 500.0,
            "fuse_capacity": 100.0,
            "switch_capacity": 100.0,
            "iron_losses_kw": 45.0,
            "copper_losses_kw": 60.0,
            "connection_date": "2020-01-15",
            "geometry": {"type": "Point", "coordinates": [-46.6350, -23.5500]}
        },
        {
            "code": "TR-001-B",
            "distributor_code": "001",
            "description": "Transformador Centro B",
            "geodatabase_id": gdb_id,
            "connection_phases": "ABC",
            "status": "SM",
            "unit_type": "51",
            "position": "D",
            "location_area": "1",
            "configuration": "RA",
            "substation": se_centro,
            "nominal_power_kva": 300.0,
            "fuse_capacity": 80.0,
            "switch_capacity": 80.0,
            "iron_losses_kw": 85.0,
            "copper_losses_kw": 90.0,
            "connection_date": "2019-06-10",
            "geometry": {"type": "Point", "coordinates": [-46.6348, -23.5498]}
        },
        {
            "code": "TR-001-C",
            "distributor_code": "001",
            "description": "Transformador Centro C",
            "geodatabase_id": gdb_id,
            "connection_phases": "ABCN",
            "status": "SM",
            "unit_type": "51",
            "position": "D",
            "location_area": "1",
            "configuration": "RA",
            "substation": se_centro,
            "nominal_power_kva": 750.0,
            "fuse_capacity": 150.0,
            "switch_capacity": 150.0,
            "iron_losses_kw": 30.0,
            "copper_losses_kw": 35.0,
            "connection_date": "2022-08-01",
            "geometry": {"type": "Point", "coordinates": [-46.6352, -23.5502]}
        },
        {
            "code": "TR-002-A",
            "distributor_code": "001",
            "description": "Transformador Norte A",
            "geodatabase_id": gdb_id,
            "connection_phases": "ABC",
            "status": "SM",
            "unit_type": "51",
            "position": "D",
            "location_area": "1",
            "configuration": "RA",
            "substation": se_norte,
            "nominal_power_kva": 250.0,
            "fuse_capacity": 60.0,
            "switch_capacity": 60.0,
            "iron_losses_kw": 30.0,
            "copper_losses_kw": 40.0,
            "connection_date": "2021-03-20",
            "geometry": {"type": "Point", "coordinates": [-46.6410, -23.5070]}
        },
        {
            "code": "TR-002-B",
            "distributor_code": "001",
            "description": "Transformador Norte B",
            "geodatabase_id": gdb_id,
            "connection_phases": "ABC",
            "status": "SM",
            "unit_type": "51",
            "position": "D",
            "location_area": "2",
            "configuration": "RA",
            "substation": se_norte,
            "nominal_power_kva": 200.0,
            "fuse_capacity": 50.0,
            "switch_capacity": 50.0,
            "iron_losses_kw": 95.0,
            "copper_losses_kw": 110.0,
            "connection_date": "2018-11-05",
            "geometry": {"type": "Point", "coordinates": [-46.6408, -23.5068]}
        },
        {
            "code": "TR-003-A",
            "distributor_code": "001",
            "description": "Transformador Sul A",
            "geodatabase_id": gdb_id,
            "connection_phases": "ABC",
            "status": "SM",
            "unit_type": "51",
            "position": "D",
            "location_area": "2",
            "configuration": "RA",
            "substation": se_sul,
            "nominal_power_kva": 400.0,
            "fuse_capacity": 90.0,
            "switch_capacity": 90.0,
            "iron_losses_kw": 105.0,
            "copper_losses_kw": 120.0,
            "connection_date": "2017-04-12",
            "geometry": {"type": "Point", "coordinates": [-46.6370, -23.6070]}
        }
    ]

    # ===========================================================================
    # MT NETWORK SEGMENTS
    # FIX: SEG-MT-002 começa em ponto diferente do SEG-MT-001
    #      para evitar duplicate key no índice geo 2dsphere
    # ===========================================================================
    mt_network_segments = [
        {
            "code": "SEG-MT-001",
            "distributor_code": "001",
            "description": "Segmento MT Centro 1",
            "geodatabase_id": gdb_id,
            "feeder_code": feeder_centro_1,
            "connection_point_start": se_centro,
            "connection_point_end": "TR-001-A",
            "connection_phases": "ABC",
            "voltage_level_code": 13,
            "length_m": 850.0,
            "shape_length": 850.0,
            "phase_conductor": {"material": "AL", "insulation": "XLPE", "ampacity": 300.0, "type": "CAA"},
            "neutral_conductor": {"material": "AL", "insulation": "XLPE", "ampacity": 150.0, "type": "CAA"},
            "geometry": {
                "type": "MultiLineString",
                "coordinates": [[[-46.6360, -23.5510], [-46.6355, -23.5505], [-46.6350, -23.5500]]]
            }
        },
        {
            "code": "SEG-MT-002",
            "distributor_code": "001",
            "description": "Segmento MT Centro 2",
            "geodatabase_id": gdb_id,
            "feeder_code": feeder_centro_2,
            "connection_point_start": se_centro,
            "connection_point_end": "TR-001-B",
            "connection_phases": "ABC",
            "voltage_level_code": 13,
            "length_m": 620.0,
            "shape_length": 620.0,
            "phase_conductor": {"material": "AL", "insulation": "XLPE", "ampacity": 250.0, "type": "CAA"},
            "neutral_conductor": {"material": "AL", "insulation": "XLPE", "ampacity": 120.0, "type": "CAA"},
            "geometry": {
                "type": "MultiLineString",
                "coordinates": [[[-46.6320, -23.5480], [-46.6330, -23.5490], [-46.6348, -23.5498]]]
            }
        },
        {
            "code": "SEG-MT-003",
            "distributor_code": "001",
            "description": "Segmento MT Norte 1",
            "geodatabase_id": gdb_id,
            "feeder_code": feeder_norte_1,
            "connection_point_start": se_norte,
            "connection_point_end": "TR-002-A",
            "connection_phases": "ABC",
            "voltage_level_code": 13,
            "length_m": 1100.0,
            "shape_length": 1100.0,
            "phase_conductor": {"material": "CU", "insulation": "PVC", "ampacity": 200.0, "type": "Nu"},
            "neutral_conductor": {"material": "CU", "insulation": "PVC", "ampacity": 100.0, "type": "Nu"},
            "geometry": {
                "type": "MultiLineString",
                "coordinates": [[[-46.6420, -23.5080], [-46.6415, -23.5075], [-46.6410, -23.5070]]]
            }
        },
        {
            "code": "SEG-MT-004",
            "distributor_code": "001",
            "description": "Segmento MT Sul 1",
            "geodatabase_id": gdb_id,
            "feeder_code": feeder_sul_1,
            "connection_point_start": se_sul,
            "connection_point_end": "TR-003-A",
            "connection_phases": "ABCN",
            "voltage_level_code": 13,
            "length_m": 780.0,
            "shape_length": 780.0,
            "phase_conductor": {"material": "AL", "insulation": "XLPE", "ampacity": 280.0, "type": "CAA"},
            "neutral_conductor": {"material": "AL", "insulation": "XLPE", "ampacity": 140.0, "type": "CAA"},
            "geometry": {
                "type": "MultiLineString",
                "coordinates": [[[-46.6380, -23.6080], [-46.6375, -23.6075], [-46.6370, -23.6070]]]
            }
        },
        {
            "code": "SEG-MT-005",
            "distributor_code": "001",
            "description": "Segmento MT Centro 3",
            "geodatabase_id": gdb_id,
            "feeder_code": feeder_centro_1,
            "connection_point_start": "TR-001-A",
            "connection_point_end": "TR-001-C",
            "connection_phases": "ABCN",
            "voltage_level_code": 13,
            "length_m": 450.0,
            "shape_length": 450.0,
            "phase_conductor": {"material": "AL", "insulation": "XLPE", "ampacity": 350.0, "type": "CAA"},
            "neutral_conductor": {"material": "AL", "insulation": "XLPE", "ampacity": 175.0, "type": "CAA"},
            "geometry": {
                "type": "MultiLineString",
                "coordinates": [[[-46.6350, -23.5500], [-46.6351, -23.5501], [-46.6352, -23.5502]]]
            }
        }
    ]

    # ===========================================================================
    # AT NETWORK SEGMENTS
    # ===========================================================================
    at_network_segments = [
        {
            "code": "SEG-AT-001",
            "distributor_code": "001",
            "description": "Segmento AT Centro-Norte",
            "geodatabase_id": gdb_id,
            "feeder_code": feeder_centro_1,
            "connection_point_start": se_centro,
            "connection_point_end": se_norte,
            "connection_phases": "ABC",
            "voltage_level_code": 138,
            "length_m": 3200.0,
            "shape_length": 3200.0,
            "phase_conductor": {"material": "AL", "insulation": "Nu", "ampacity": 600.0, "type": "CAA"},
            "neutral_conductor": {"material": "AL", "insulation": "Nu", "ampacity": 300.0, "type": "CAA"},
            "geometry": {
                "type": "MultiLineString",
                "coordinates": [[[-46.6362, -23.5512], [-46.6390, -23.5300], [-46.6420, -23.5080]]]
            }
        },
        {
            "code": "SEG-AT-002",
            "distributor_code": "001",
            "description": "Segmento AT Centro-Sul",
            "geodatabase_id": gdb_id,
            "feeder_code": feeder_centro_2,
            "connection_point_start": se_centro,
            "connection_point_end": se_sul,
            "connection_phases": "ABC",
            "voltage_level_code": 138,
            "length_m": 4100.0,
            "shape_length": 4100.0,
            "phase_conductor": {"material": "AL", "insulation": "Nu", "ampacity": 600.0, "type": "CAA"},
            "neutral_conductor": {"material": "AL", "insulation": "Nu", "ampacity": 300.0, "type": "CAA"},
            "geometry": {
                "type": "MultiLineString",
                "coordinates": [[[-46.6342, -23.5512], [-46.6368, -23.5800], [-46.6380, -23.6080]]]
            }
        },
        {
            "code": "SEG-AT-003",
            "distributor_code": "001",
            "description": "Segmento AT Norte-Sul",
            "geodatabase_id": gdb_id,
            "feeder_code": feeder_norte_1,
            "connection_point_start": se_norte,
            "connection_point_end": se_sul,
            "connection_phases": "ABCN",
            "voltage_level_code": 138,
            "length_m": 6500.0,
            "shape_length": 6500.0,
            "phase_conductor": {"material": "AL", "insulation": "Nu", "ampacity": 600.0, "type": "CAA"},
            "neutral_conductor": {"material": "AL", "insulation": "Nu", "ampacity": 300.0, "type": "CAA"},
            "geometry": {
                "type": "MultiLineString",
                "coordinates": [[[-46.6420, -23.5080], [-46.6400, -23.5600], [-46.6380, -23.6080]]]
            }
        }
    ]

    # ===========================================================================
    # CONSUMER UNITS PJ
    # ===========================================================================
    consumer_units_pj = [
        {
            "encrypted_id": "ENC-UC-001",
            "voltage_level": "MT",
            "distributor_code": 1,
            "service_point": "PAC-001",
            "mt_segment_code": "SEG-MT-001",
            "at_transformer_unit": "TR-001-A",
            "no_network": None,
            "base_date": "2024-01-01",
            "substation": se_centro,
            "uc_set": 1001,
            "municipality_code": 3550308,
            "sub_class": "IN",
            "cnae": "3514000",
            "voltage_group": "MT",
            "supply_voltage_kv": 13,
            "tariff_group": "A4",
            "status": "AT",
            "connection_date": "2018-03-10",
            "system_type": "RD_INTERLIG",
            "contracted_demand_kw": 500,
            "location_area": "UB",
            "demand": {"total": [480.0, 490.0, 510.0, 520.0, 500.0, 480.0, 470.0, 490.0, 510.0, 530.0, 520.0, 500.0]},
            "energy": {"total": [34560.0, 35280.0, 36720.0, 37440.0, 36000.0, 34560.0, 33840.0, 35280.0, 36720.0, 38160.0, 37440.0, 36000.0]},
            "dic": [0.5, 0.0, 1.2, 0.0, 0.3, 0.0, 0.8, 0.0, 0.0, 0.5, 0.0, 0.2],
            "fic": [1.0, 0.0, 2.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0],
            "location": {"type": "Point", "coordinates": [-46.6345, -23.5497]}
        },
        {
            "encrypted_id": "ENC-UC-002",
            "voltage_level": "MT",
            "distributor_code": 1,
            "service_point": "PAC-002",
            "mt_segment_code": "SEG-MT-001",
            "at_transformer_unit": "TR-001-A",
            "no_network": None,
            "base_date": "2024-01-01",
            "substation": se_centro,
            "uc_set": 1001,
            "municipality_code": 3550308,
            "sub_class": "SP2",
            "cnae": "4711302",
            "voltage_group": "MT",
            "supply_voltage_kv": 13,
            "tariff_group": "A4",
            "status": "AT",
            "connection_date": "2019-07-22",
            "system_type": "RD_INTERLIG",
            "contracted_demand_kw": 300,
            "location_area": "UB",
            "demand": {"total": [290.0, 295.0, 300.0, 310.0, 305.0, 295.0, 285.0, 290.0, 300.0, 315.0, 310.0, 300.0]},
            "energy": {"total": [20880.0, 21240.0, 21600.0, 22320.0, 21960.0, 21240.0, 20520.0, 20880.0, 21600.0, 22680.0, 22320.0, 21600.0]},
            "dic": [0.0, 0.5, 0.0, 1.0, 0.0, 0.5, 0.0, 0.0, 0.8, 0.0, 0.3, 0.0],
            "fic": [0.0, 1.0, 0.0, 2.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0],
            "location": {"type": "Point", "coordinates": [-46.6342, -23.5498]}
        },
        {
            "encrypted_id": "ENC-UC-003",
            "voltage_level": "AT",
            "distributor_code": 1,
            "service_point": "PAC-003",
            "at_transformer_code": 101,
            "substation": se_centro,
            "uc_set": 1002,
            "municipality_code": 3550308,
            "sub_class": "IN",
            "cnae": "2411300",
            "connection_contract_type": "A2-Tipo1",
            "voltage_group": "AT",
            "supply_voltage_kv": 138,
            "tariff_group": "A2",
            "status": "AT",
            "connection_date": "2015-01-10",
            "system_type": "RD_INTERLIG",
            "contracted_demand_kw": 2000,
            "location_area": "UB",
            "demand": {
                "peak":     [1900.0, 1950.0, 2000.0, 2050.0, 1980.0, 1900.0, 1850.0, 1900.0, 1980.0, 2100.0, 2050.0, 2000.0],
                "off_peak": [1200.0, 1250.0, 1300.0, 1350.0, 1280.0, 1200.0, 1150.0, 1200.0, 1280.0, 1400.0, 1350.0, 1300.0]
            },
            "energy": {
                "peak":     [136800.0, 140400.0, 144000.0, 147600.0, 142560.0, 136800.0, 133200.0, 136800.0, 142560.0, 151200.0, 147600.0, 144000.0],
                "off_peak": [86400.0, 90000.0, 93600.0, 97200.0, 92160.0, 86400.0, 82800.0, 86400.0, 92160.0, 100800.0, 97200.0, 93600.0]
            },
            "dic": [0.0, 0.0, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0],
            "fic": [0.0, 0.0, 1.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            "location": {"type": "Point", "coordinates": [-46.6355, -23.5505]}
        },
        {
            "encrypted_id": "ENC-UC-004",
            "voltage_level": "MT",
            "distributor_code": 1,
            "service_point": "PAC-004",
            "mt_segment_code": "SEG-MT-003",
            "at_transformer_unit": "TR-002-A",
            "no_network": None,
            "base_date": "2024-01-01",
            "substation": se_norte,
            "uc_set": 2001,
            "municipality_code": 3534401,
            "sub_class": "IN",
            "cnae": "1811301",
            "voltage_group": "MT",
            "supply_voltage_kv": 13,
            "tariff_group": "A4",
            "status": "AT",
            "connection_date": "2020-09-15",
            "system_type": "RD_INTERLIG",
            "contracted_demand_kw": 400,
            "location_area": "UB",
            "demand": {"total": [380.0, 385.0, 395.0, 400.0, 390.0, 380.0, 370.0, 380.0, 390.0, 405.0, 400.0, 395.0]},
            "energy": {"total": [27360.0, 27720.0, 28440.0, 28800.0, 28080.0, 27360.0, 26640.0, 27360.0, 28080.0, 29160.0, 28800.0, 28440.0]},
            "dic": [0.3, 0.0, 0.0, 0.8, 0.0, 0.0, 0.5, 0.0, 0.0, 0.3, 0.0, 0.0],
            "fic": [1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            "location": {"type": "Point", "coordinates": [-46.6412, -23.5072]}
        },
        {
            "encrypted_id": "ENC-UC-005",
            "voltage_level": "MT",
            "distributor_code": 1,
            "service_point": "PAC-005",
            "mt_segment_code": "SEG-MT-004",
            "at_transformer_unit": "TR-003-A",
            "no_network": None,
            "base_date": "2024-01-01",
            "substation": se_sul,
            "uc_set": 3001,
            "municipality_code": 3548708,
            "sub_class": "SP2",
            "cnae": "4711302",
            "voltage_group": "MT",
            "supply_voltage_kv": 13,
            "tariff_group": "A4",
            "status": "AT",
            "connection_date": "2016-05-30",
            "system_type": "RD_INTERLIG",
            "contracted_demand_kw": 600,
            "location_area": "NU",
            "demand": {"total": [570.0, 580.0, 595.0, 600.0, 585.0, 570.0, 560.0, 575.0, 590.0, 605.0, 600.0, 595.0]},
            "energy": {"total": [41040.0, 41760.0, 42840.0, 43200.0, 42120.0, 41040.0, 40320.0, 41400.0, 42480.0, 43560.0, 43200.0, 42840.0]},
            "dic": [0.0, 0.8, 0.0, 0.0, 1.5, 0.0, 0.0, 0.5, 0.0, 0.0, 0.8, 0.0],
            "fic": [0.0, 1.0, 0.0, 0.0, 2.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0],
            "location": {"type": "Point", "coordinates": [-46.6372, -23.6072]}
        },
        {
            "encrypted_id": "ENC-UC-006",
            "voltage_level": "MT",
            "distributor_code": 1,
            "service_point": "PAC-006",
            "mt_segment_code": "SEG-MT-002",
            "at_transformer_unit": "TR-001-B",
            "no_network": None,
            "base_date": "2024-01-01",
            "substation": se_centro,
            "uc_set": 1001,
            "municipality_code": 3550308,
            "sub_class": "IN",
            "cnae": "6201501",
            "voltage_group": "MT",
            "supply_voltage_kv": 13,
            "tariff_group": "A4",
            "status": "DS",
            "connection_date": "2017-11-20",
            "system_type": "RD_INTERLIG",
            "contracted_demand_kw": 200,
            "location_area": "UB",
            "demand": {"total": [None] * 12},
            "energy": {"total": [None] * 12},
            "dic": [None] * 12,
            "fic": [None] * 12,
            "location": {"type": "Point", "coordinates": [-46.6346, -23.5496]}
        }
    ]

    energy_losses_tariff = [
            {
                "distributor": "ENEL SP",
                "distributor_slug": "ENEL SP",
                "state": "São Paulo",
                "uf": "SP",
                "process_date": "2023-01-01",
                "tme_brl_mwh": 312.50,
                "basic_network_loss_mwh": 120000.0,
                "technical_loss_mwh": 850000.0,
                "non_technical_loss_mwh": 430000.0,
                "basic_network_loss_cost_brl": 37500000.0,
                "technical_loss_cost_brl": 265625000.0,
                "non_technical_loss_cost_brl": 134375000.0,
                "parcel_b_brl": 980000000.0,
                "required_revenue_brl": 4200000000.0
            },
            {
                "distributor": "ENEL SP",
                "distributor_slug": "ENEL SP",
                "state": "São Paulo",
                "uf": "SP",
                "process_date": "2021-01-01",
                "tme_brl_mwh": 289.30,
                "basic_network_loss_mwh": 115000.0,
                "technical_loss_mwh": 820000.0,
                "non_technical_loss_mwh": 410000.0,
                "basic_network_loss_cost_brl": 33269500.0,
                "technical_loss_cost_brl": 237226000.0,
                "non_technical_loss_cost_brl": 118613000.0,
                "parcel_b_brl": 920000000.0,
                "required_revenue_brl": 3950000000.0
            },
            {
                "distributor": "CPFL Paulista",
                "distributor_slug": "CPFL Paulista",
                "state": "São Paulo",
                "uf": "SP",
                "process_date": "2023-06-01",
                "tme_brl_mwh": 298.75,
                "basic_network_loss_mwh": 95000.0,
                "technical_loss_mwh": 620000.0,
                "non_technical_loss_mwh": 180000.0,
                "basic_network_loss_cost_brl": 28381250.0,
                "technical_loss_cost_brl": 185225000.0,
                "non_technical_loss_cost_brl": 53775000.0,
                "parcel_b_brl": 760000000.0,
                "required_revenue_brl": 3100000000.0
            },
            {
                "distributor": "CPFL Paulista",
                "distributor_slug": "CPFL Paulista",
                "state": "São Paulo",
                "uf": "SP",
                "process_date": "2020-06-01",
                "tme_brl_mwh": 265.40,
                "basic_network_loss_mwh": 92000.0,
                "technical_loss_mwh": 600000.0,
                "non_technical_loss_mwh": 170000.0,
                "basic_network_loss_cost_brl": 24416800.0,
                "technical_loss_cost_brl": 159240000.0,
                "non_technical_loss_cost_brl": 45118000.0,
                "parcel_b_brl": 710000000.0,
                "required_revenue_brl": 2850000000.0
            },
            {
                "distributor": "Amazonas Energia",
                "distributor_slug": "Amazonas Energia",
                "state": "Amazonas",
                "uf": "AM",
                "process_date": "2023-11-01",
                "tme_brl_mwh": 195.17,
                "basic_network_loss_mwh": 95581.132,
                "technical_loss_mwh": 786836.937,
                "non_technical_loss_mwh": 3269260.0,
                "basic_network_loss_cost_brl": 18655010.0,
                "technical_loss_cost_brl": 153570600.0,
                "non_technical_loss_cost_brl": 638076500.0,
                "parcel_b_brl": 386332500.0,
                "required_revenue_brl": 2847472000.0
            },
            {
                "distributor": "Celesc",
                "distributor_slug": "Celesc",
                "state": "Santa Catarina",
                "uf": "SC",
                "process_date": "2023-08-01",
                "tme_brl_mwh": 278.90,
                "basic_network_loss_mwh": 78000.0,
                "technical_loss_mwh": 510000.0,
                "non_technical_loss_mwh": 95000.0,
                "basic_network_loss_cost_brl": 21754200.0,
                "technical_loss_cost_brl": 142239000.0,
                "non_technical_loss_cost_brl": 26495500.0,
                "parcel_b_brl": 620000000.0,
                "required_revenue_brl": 2400000000.0
            },
            {
                "distributor": "Cemig",
                "distributor_slug": "Cemig",
                "state": "Minas Gerais",
                "uf": "MG",
                "process_date": "2023-04-01",
                "tme_brl_mwh": 305.60,
                "basic_network_loss_mwh": 210000.0,
                "technical_loss_mwh": 1450000.0,
                "non_technical_loss_mwh": 520000.0,
                "basic_network_loss_cost_brl": 64176000.0,
                "technical_loss_cost_brl": 443120000.0,
                "non_technical_loss_cost_brl": 158912000.0,
                "parcel_b_brl": 1850000000.0,
                "required_revenue_brl": 7800000000.0
            },
            {
                "distributor": "Coelba",
                "distributor_slug": "Coelba",
                "state": "Bahia",
                "uf": "BA",
                "process_date": "2022-09-01",
                "tme_brl_mwh": 267.30,
                "basic_network_loss_mwh": 145000.0,
                "technical_loss_mwh": 980000.0,
                "non_technical_loss_mwh": 1250000.0,
                "basic_network_loss_cost_brl": 38758500.0,
                "technical_loss_cost_brl": 261954000.0,
                "non_technical_loss_cost_brl": 334125000.0,
                "parcel_b_brl": 1120000000.0,
                "required_revenue_brl": 4650000000.0
            }
    ]
    # ===========================================================================
    # INSERT
    # ===========================================================================
    collections = {
        "municipalities":            municipalities,
        "substations":               substations,
        "distribution_transformers": distribution_transformers,
        "mt_network_segments":       mt_network_segments,
        "at_network_segments":       at_network_segments,
        "consumer_units_pj":         consumer_units_pj,
        "energy_losses_tariff":      energy_losses_tariff
    }

    for collection_name, documents in collections.items():
        try:
            result = db[collection_name].insert_many(documents)
            print(f"✅ {collection_name}: {len(result.inserted_ids)} documentos inseridos")
        except Exception as e:
            print(f"❌ {collection_name}: {type(e).__name__}: {e}")

    print("\nSeed concluído.")

if __name__ == "__main__":
    seed()