import os
import logging
from pymongo.collection import Collection
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 1000

def load_limits(
    transform_result: dict,
    conj_collection: Collection,
) -> dict:
    docs = transform_result.get("valid", [])
    logger.info(f"[load_limits] {len(docs)} documentos recebidos.")

    operations = []

    for doc in docs:
        code                = doc.get("code")
        indicator_type_code = doc.get("indicator_type_code")
        year                = doc.get("year")
        limit               = doc.get("limit")

        if not code or not indicator_type_code or year is None:
            continue

        entry = {
            "indicator_type_code": indicator_type_code,
            "year":                year,
            "limit":               limit,
            "accumulated_value":   None,
            "periods_count":       1,
            "status":              "partial",
            "criticality":         None,
        }

        operations.append(
            UpdateOne(
                {
                    "code": code,
                    "annual_summaries": {
                        "$not": {
                            "$elemMatch": {
                                "indicator_type_code": indicator_type_code,
                                "year":               year,
                            }
                        }
                    }
                },
                {"$push": {"annual_summaries": entry}},
                upsert=False
            )
        )

    total_modified = 0
    total_rejected = 0

    if operations:
        batch_size = int(os.getenv("ETL_BULK_PERSIST_BATCH_SIZE", DEFAULT_BATCH_SIZE))
        try:
            for i in range(0, len(operations), batch_size):
                batch = operations[i:i + batch_size]
                result = conj_collection.bulk_write(batch, ordered=False)
                total_modified += result.modified_count
                logger.info(
                    f"[load_limits] conj.annual_summaries batch {i//batch_size + 1} — "
                    f"matched: {result.matched_count}, modified: {result.modified_count}"
                )
        except BulkWriteError as e:
            total_rejected += len(e.details.get("writeErrors", []))
            total_modified += e.details.get("nModified", 0)
            logger.error(f"[load_limits] BulkWriteError em conj: {e.details}")

    metrics = {
        "inserted": 0,
        "updated":  total_modified,
        "matched":  0,
        "rejected": total_rejected,
    }

    logger.info(f"[load_limits] {metrics}")
    return metrics