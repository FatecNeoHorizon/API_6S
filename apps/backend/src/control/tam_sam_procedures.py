from datetime import datetime, timezone
from typing import Optional

import pymongo

from src.config.settings import Settings
from src.database.connection import get_client

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
        pipeline = [
            {"$match": {"consumer_unit_set_id": {"$nin": [None, ""]}}},
            {"$group": {"_id": "$consumer_unit_set_id"}},
            {"$count": "tam_total"},
        ]

        result = list(self.db.distribution_indices.aggregate(pipeline, allowDiskUse=True))
        tam_total = int(result[0]["tam_total"]) if result else 0

        calculated_on = datetime.now(timezone.utc)

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
