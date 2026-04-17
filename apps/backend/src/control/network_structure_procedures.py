from pymongo import MongoClient
from src.etl.database import get_client
from src.config.settings import Settings
from src.model.network_structure_model import (
    NetworkSummary,
    NetworkAsset,
    NetworkTransformerDetail,
    SubstationDetail
)
from typing import List, Optional
from pydantic import TypeAdapter
import pymongo

ALERT_THRESHOLD_KW = 100

# Get settings for database name
_settings = Settings()

class NetworkStructureProcedures():
    connection: Optional[pymongo.MongoClient]
    db: Optional[pymongo.database.Database]

    def __init__(self, connection: Optional[pymongo.MongoClient] = None):
        """
        Initialize procedures with optional MongoDB connection.
        
        Args:
            connection: MongoDB client instance. If not provided, a new connection is created.
                       Prefer to pass the shared connection from app.mongodb to reuse the pool.
        """
        if connection is not None:
            self.connection = connection
        else:
            # Fallback: create new connection (for backward compatibility)
            self.connection = get_client()
        
        self.db = self.connection[_settings.mongo_db_name]

    def _define_transformer_status(self,transformer: dict):
        if transformer.get("status") == "SM":
            iron_losses = 0
            copper_losses = 0
            if transformer["iron_losses_kw"] is not None:
                iron_losses = transformer.get("iron_losses_kw")
            if transformer["copper_losses_kw"] is not None:
                copper_losses = transformer.get("copper_losses_kw")
            losses_sum = iron_losses + copper_losses
            if losses_sum >= ALERT_THRESHOLD_KW:
                return "Alert"
            return "Operational"
        return "Inactive"

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

        qtd_operational = qtd_operational - qtd_alert

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
                    status=self._define_transformer_status(t),
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