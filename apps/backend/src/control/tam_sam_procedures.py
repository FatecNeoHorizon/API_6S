from datetime import datetime, timezone
from typing import Optional, List
from pydantic import TypeAdapter

import pymongo

from src.config.settings import Settings
from src.database.connection import get_client
from src.utils.clean_filter import clean_filter, remove_operators_fields

_settings = Settings()


class Tam_sam_procedures:
    connection: Optional[pymongo.MongoClient]
    db: Optional[pymongo.database.Database]

    def __init__(self, connection: Optional[pymongo.MongoClient] = None):
        if connection is not None:
            self.connection = connection
        else:
            self.connection = get_client()

        self.db = self.connection[_settings.mongo_db_name]

    def calculate_and_persist_tam_total(self):
        # TAM is the number of distinct consumer unit sets in the indicators collection.
        pipeline = [
            {"$match": {"consumer_unit_set_id": {"$nin": [None, ""]}}},
            {"$group": {"_id": "$consumer_unit_set_id"}},
            {"$count": "tam_total"},
        ]

        result = list(self.db.distribution_indices.aggregate(pipeline, allowDiskUse=True))
        tam_total = int(result[0]["tam_total"]) if result else 0

        calculated_on = datetime.now(timezone.utc)

        # Upsert keeps a single logical TAM record and replaces it on reprocessing.
        self.db.tam_sam.update_one(
            {"metric": "tam_total"},
            {
                "$set": {
                    "metric": "tam_total",
                    "tam_total": tam_total,
                    "calculated_on": calculated_on,
                }
            },
            upsert=True,
        )

        return {
            "tam_total": tam_total,
            "calculated_on": calculated_on.isoformat().replace("+00:00", "Z"),
        }

    def get_tam_total(self):
        doc = self.db.tam_sam.find_one(
            {"metric": "tam_total"},
            {"_id": 0, "tam_total": 1, "calculated_on": 1},
        )

        if not doc:
            return None

        calculated_on = doc.get("calculated_on")
        if isinstance(calculated_on, datetime):
            doc["calculated_on"] = calculated_on.isoformat().replace("+00:00", "Z")

        return doc
    
    def get_sam_total(self, year):

        pipeline = [
            {"$match": {"annual_summaries.year": year}},
            {"$match": {"$expr": {"$gt": ["$annual_summaries.accumulated_value", "$annual_summaries.limit"]}}},
            {"$group": {"_id": {"conj": "$code"}}},
            {"$count": "sam_total"},
        ]

        result = list(self.db.conj.aggregate(pipeline, allowDiskUse=True))
        sam_total = int(result[0]["sam_total"]) if result else 0

        return sam_total

    def get_sam_top_ten(self, year, indicator_type_code):
        pipeline = [
            {"$match": {"annual_summaries.year": year}},
            {"$match": {"annual_summaries.indicator_type_code": indicator_type_code}},
            {"$match": {"$expr": {"$gt": ["$annual_summaries.accumulated_value", "$annual_summaries.limit"]}}},
            {"$project": { "_id": 0, "shape_length": 0, "shape_area": 0, "arat_id": 0, "geodatabase_id": 0, "geometry": 0, "distribution_indices": 0} },
            {"$sort": {"annual_summaries.accumulated_value": -1}},
            {"$limit": 10}
        ]

        cursor = self.db.conj.aggregate(pipeline, allowDiskUse=True)

        result = cursor.to_list()

        return result
