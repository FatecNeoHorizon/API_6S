import logging
from pymongo.collection import Collection
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

logger = logging.getLogger(__name__)

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

        # Só faz push se ainda não existe entrada com essa chave composta
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
        try:
            result = conj_collection.bulk_write(operations, ordered=False)
            total_modified = result.modified_count
            logger.info(
                f"[load_limits] conj.annual_summaries — "
                f"matched: {result.matched_count}, modified: {result.modified_count}"
            )
        except BulkWriteError as e:
            total_rejected = len(e.details.get("writeErrors", []))
            total_modified = e.details.get("nModified", 0)
            logger.error(f"[load_limits] BulkWriteError em conj: {e.details}")

    metrics = {
        "inserted": 0,
        "updated":  total_modified,
        "matched":  0,
        "rejected": total_rejected,
    }

    logger.info(f"[load_limits] {metrics}")
    return metrics