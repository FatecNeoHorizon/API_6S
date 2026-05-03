import logging
from pymongo.collection import Collection
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from src.etl.utils.bulk_persist import bulk_persist

logger = logging.getLogger(__name__)

FILTER_KEYS = [
    "agent_acronym",
    "consumer_unit_set_id",
    "indicator_type_code",
    "year",
    "period",
]

def load_decfec(
        transform_result: dict,
        collection: Collection,
        conj_collection: Collection
) -> dict:
    docs = transform_result.get("valid", [])
    logger.info(f"[load_decfec] {len(docs)} documentos recebidos.")

    # 1. Persistência em distribution_indices
    metrics = bulk_persist(collection, docs, FILTER_KEYS)

    # 2. Embute em conj.distribution_indices
    operations = []
    for doc in docs:
        code = doc.get("consumer_unit_set_id")
        if not code:
            logger.warning(f"[load_decfec] Documento ignorado para embed por falta de 'consumer_unit_set_id': {doc}")
            continue

        entry = {
            "indicator_type_code": doc.get("indicator_type_code"),
            "year":                doc.get("year"),
            "period":              doc.get("period"),
            "value":               doc.get("value"),
        }

        # Só faz push se ainda não existe entrada com essa chave composta
        operations.append(
            UpdateOne(
                {
                    "code": code,
                    "distribution_indices": {
                        "$not": {
                            "$elemMatch": {
                                "indicator_type_code": entry["indicator_type_code"],
                                "year":               entry["year"],
                                "period":             entry["period"],
                            }
                        }
                    }
                },
                {"$push": {"distribution_indices": entry}},
                upsert=False
            )
        )

    if operations:
        try:
            result = conj_collection.bulk_write(operations, ordered=False)
            logger.info(
                f"[load_decfec] conj.distribution_indices — "
                f"matched: {result.matched_count}, modified: {result.modified_count}"
            )
        except BulkWriteError as e:
            logger.error(f"[load_decfec] BulkWriteError em conj: {e.details}")

    return metrics