from pymongo import MongoClient
from src.etl.database import get_client
from src.model.network_structure_model import (
    NetworkSummary,
    NetworkAsset,
    NetworkTransformerDetail,
    SubstationDetail
)
from typing import List
from pydantic import TypeAdapter
import os

ALERT_THRESHOLD_KW = 100

class NetworkStructureProcedures():
    connection : None

    def __init__(self):
        self.connection = get_client()
        self.db = self.connection[os.getenv("MONGO_DB_NAME")]

    def get_summary(self) -> NetworkSummary:
        qtd_substations = self.db["substations"].count_documents({})
        qtd_transformers = self.db["distribution_transformers"].count_documents({})
        qtd_operational = self.db["distribution_transformers"].count_documents({
            "status":"SM"
        })
        qtd_alert = self.db["distribution_transformers"].count_documents({
            "status":"SM",
            "$expr": {
                "$gt":[
                    {"$add": [
                        {"$ifNull": ["$iron_losses_kw", 0]},
                        {"$ifNull":["$copper_losses_kw", 0]}
                    ]},
                    ALERT_THRESHOLD_KW
                ]
            }
        })
        return NetworkSummary(
            substations=qtd_substations,
            transformers=qtd_transformers,
            operational=qtd_operational,
            alerts=qtd_alert
        )

    def get_assets(self, region=None, type=None, status=None) -> List[NetworkAsset]:
        transformer_filter = {}
        substations_filter = {}

        if region:
            transformer_filter["location_area"] = region
        if status:
            transformer_filter["status"] = status

        projection = {
            "code": 1,
            "description": 1,
            "location_area": 1,
            "status": 1,
            "iron_losses_kw": 1,
            "copper_losses_kw": 1,
            "geometry.coordinates": 1
        }

        result = []
    
        if type is None or type == "transformer":
            transformers = self.db["distribution_transformers"].find(
                transformer_filter, projection
            )
            for t in transformers:
                result.append(NetworkAsset(
                    type="transformer",
                    code=t.get("code"),
                    description=t.get("description"),
                    region="Urbana" if t.get("location_area") == "1" else "Rural",
                    tension=t.get("nominal_power_kva"),
                    status="Operational" if t.get("status") == "SM" else "Inactive",
                    load_kw=(t.get("iron_losses_kw") or 0) + (t.get("copper_losses_kw") or 0),
                    coordinates=t.get("geometry", {}).get("coordinates")
                ))
        if type is None or type == "substation":
            substations = self.db["substations"].find(substations_filter, projection)
            for s in substations:
                result.append(NetworkAsset(
                    type="substation",
                    code=s.get("code"),
                    description=s.get("description"),
                    region=None,
                    tension=None,
                    status=None,
                    load_kw=None,
                    coordinates=None
                ))

        return result
    
    def get_transformer_detail(self, transformer_id) -> NetworkTransformerDetail:
        transformer = self.db["distribution_transformers"].find_one(
            {"code": transformer_id},
            {
                "code": 1,
                "description": 1,
                "status": 1,
                "location_area": 1,
                "nominal_power_kva": 1,
                "iron_losses_kw": 1,
                "copper_losses_kw": 1,
                "connection_phases": 1,
                "substation": 1,
                "geometry": 1
            }
        )

        if transformer is None:
            return None

        return NetworkTransformerDetail(
            code=transformer.get("code"),
            description=transformer.get("description"),
            status=transformer.get("status"),
            location_area=transformer.get("location_area"),
            nominal_power_kva=transformer.get("nominal_power_kva"),
            iron_losses_kw=transformer.get("iron_losses_kw"),
            copper_losses_kw=transformer.get("copper_losses_kw"),
            connection_phases=transformer.get("connection_phases"),
            substation=transformer.get("substation"),
            geometry=transformer.get("geometry")
        )

    def get_substation_detail(self, substation_id) -> SubstationDetail:
        pipeline = [
            {"$match": {"code": substation_id}},

            {"$lookup": {
                "from": "distribution_transformers",
                "localField": "code",
                "foreignField": "substation",
                "as": "transformers",
                "pipeline": [
                    {"$project": {"code": 1, "status": 1, "nominal_power_kva": 1}}
                ]
            }},

            {"$lookup": {
                "from": "mt_network_segments",
                "localField": "code",
                "foreignField": "feeder_code",
                "as": "feeders",
                "pipeline": [
                    {"$group": {"_id": "$feeder_code"}},
                    {"$count": "total"}
                ]
            }},

            {"$addFields": {
                "qtd_transformers": {"$size": "$transformers"},
                "qtd_feeders": {
                    "$ifNull": [{"$arrayElemAt": ["$feeders.total", 0]}, 0]
                }
            }},

            {"$project": {
                "transformers": 0,
                "feeders": 0
            }}
        ]

        result = list(self.db["substations"].aggregate(pipeline))

        if not result:
            return None

        s = result[0]

        return SubstationDetail(
            code=s.get("code"),
            description=s.get("description"),
            distributor_code=s.get("distributor_code"),
            shape_length=s.get("shape_length"),
            shape_area=s.get("shape_area"),
            geodatabase_id=s.get("geodatabase_id"),
            geometry=s.get("geometry"),
            qtd_transformers=s.get("qtd_transformers"),
            qtd_feeders=s.get("qtd_feeders")
        )