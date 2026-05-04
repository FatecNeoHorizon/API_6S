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
            return self.calculate_and_persist_tam_total()

        calculated_on = doc.get("calculated_on")
        if isinstance(calculated_on, datetime):
            doc["calculated_on"] = calculated_on.isoformat().replace("+00:00", "Z")

        return doc
    
    def get_sam_total(self, year):

        pipeline = [
            {"$unwind": "$annual_summaries"},
            {
                "$match": {
                    "annual_summaries.year": year,
                    "annual_summaries.limit": {"$ne": None},
                }
            },
            {
                "$lookup": {
                    "from": "distribution_indices",
                    "let": {
                        "code": "$code",
                        "year": "$annual_summaries.year",
                        "indicator": "$annual_summaries.indicator_type_code",
                    },
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$consumer_unit_set_id", "$$code"]},
                                        {"$eq": ["$year", "$$year"]},
                                        {"$eq": ["$indicator_type_code", "$$indicator"]},
                                    ]
                                }
                            }
                        },
                        {
                            "$group": {
                                "_id": None,
                                "value": {"$sum": {"$ifNull": ["$value", 0]}},
                                "periods_count": {"$sum": 1},
                            }
                        },
                    ],
                    "as": "indicator_totals",
                }
            },
            {
                "$set": {
                    "sam_accumulated_value": {
                        "$ifNull": [{"$first": "$indicator_totals.value"}, 0]
                    },
                    "sam_periods_count": {
                        "$ifNull": [{"$first": "$indicator_totals.periods_count"}, 0]
                    },
                }
            },
            {
                "$match": {
                    "sam_periods_count": {"$gt": 0},
                    "$expr": {
                        "$lte": ["$sam_accumulated_value", "$annual_summaries.limit"]
                    }
                }
            },
            {"$group": {"_id": "$code"}},
            {"$count": "sam_total"},
        ]

        result = list(self.db.conj.aggregate(pipeline, allowDiskUse=True))
        sam_total = int(result[0]["sam_total"]) if result else 0

        return sam_total

    def get_sam_top_ten(self, year, indicator_type_code):
        pipeline = [
            {"$unwind": "$annual_summaries"},
            {
                "$match": {
                    "annual_summaries.year": year,
                    "annual_summaries.indicator_type_code": indicator_type_code,
                    "annual_summaries.limit": {"$ne": None},
                }
            },
            {
                "$lookup": {
                    "from": "distribution_indices",
                    "let": {
                        "code": "$code",
                        "year": "$annual_summaries.year",
                        "indicator": "$annual_summaries.indicator_type_code",
                    },
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        {"$eq": ["$consumer_unit_set_id", "$$code"]},
                                        {"$eq": ["$year", "$$year"]},
                                        {"$eq": ["$indicator_type_code", "$$indicator"]},
                                    ]
                                }
                            }
                        },
                        {
                            "$group": {
                                "_id": None,
                                "value": {"$sum": {"$ifNull": ["$value", 0]}},
                                "periods_count": {"$sum": 1},
                            }
                        },
                    ],
                    "as": "indicator_totals",
                }
            },
            {
                "$set": {
                    "sam_accumulated_value": {
                        "$ifNull": [{"$first": "$indicator_totals.value"}, 0]
                    },
                    "sam_periods_count": {
                        "$ifNull": [{"$first": "$indicator_totals.periods_count"}, 0]
                    },
                }
            },
            {
                "$match": {
                    "sam_periods_count": {"$gt": 0},
                    "$expr": {
                        "$lte": ["$sam_accumulated_value", "$annual_summaries.limit"]
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "shape_length": 0,
                    "shape_area": 0,
                    "arat_id": 0,
                    "geodatabase_id": 0,
                    "geometry": 0,
                    "distribution_indices": 0,
                    "indicator_totals": 0,
                }
            },
            {"$sort": {"sam_accumulated_value": -1}},
            {"$limit": 10}
        ]

        return list(self.db.conj.aggregate(pipeline, allowDiskUse=True))
