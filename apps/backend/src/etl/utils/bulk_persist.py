import os
import logging
from pymongo.collection import Collection
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 1000

def bulk_persist(
        collection: Collection,
        docs: list,
        filter_keys: list[str],
) -> dict:
    
    if not docs:
        logger.warning(f"[bulk_persist] Nenhum documento recebido para '{collection.name}'.")
        return {"inserted": 0, "updated": 0, "matched": 0, "rejected": 0}

    batch_size = int(os.getenv("ETL_BULK_PERSIST_BATCH_SIZE", DEFAULT_BATCH_SIZE))

    total_inserted = 0
    total_updated = 0  
    total_matched = 0
    total_rejected = 0   
    chunks_completed = 0

    for i in range(0, len(docs), batch_size):
        batch = docs[i : i + batch_size]

        operations = []

        for doc in batch:
            filter = {key: doc[key] for key in filter_keys if key in doc}

            if len(filter) < len(filter_keys):
                logger.warning(f"[bulk_persist] Documento ignorado por falta de chaves de filtro: {doc}")
                total_rejected += 1
                continue

            operations.append(
                UpdateOne(filter, {"$set": doc}, upsert=True)
                )
        
        if not operations:
            continue

        try:
            result = collection.bulk_write(operations, ordered=False)
            total_inserted += result.upserted_count
            total_updated += result.modified_count
            total_matched += result.matched_count
            chunks_completed += 1
            logger.info(
                f"[bulk_persist] '{collection.name}' - Batch {chunks_completed}: "
                f"Inserted: {result.upserted_count}, "
                f"Updated: {result.modified_count}, "
                f"Matched: {result.matched_count}, "
                f"Rejected: {total_rejected}, "
                f"Chunk size: {len(operations)}"
            )
            
        except BulkWriteError as e:
            total_rejected += len(e.details.get("writeErrors", []))
            total_inserted += e.details.get("nUpserted", 0)
            total_updated += e.details.get("nUpdated", 0)
            total_matched += e.details.get("nMatched", 0)
            logger.error(f"[bulk_persist] BulkWriteError em '{collection.name}': {e.details}")

    metrics = {
        "inserted": total_inserted,
        "updated": total_updated,
        "matched": total_matched,
        "rejected": total_rejected,
    }
    logger.info(f"[bulk_persist] '{collection.name}' — {metrics}")
    return metrics