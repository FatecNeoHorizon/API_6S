import logging
from datetime import datetime, timezone
from pymongo.collection import Collection
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

logger = logging.getLogger(__name__)

FILTER_KEYS = ["consumer_unit_set_id", "indicator", "forecast_year", "forecast_period"]


def persist_predictions(
    collection: Collection,
    predictions: list[dict],
    batch_size: int = 1000,
) -> dict:
    """
    Persist predictions to MongoDB using idempotent upsert.
    
    Args:
        collection: MongoDB predictions collection
        predictions: List of prediction documents
        batch_size: Batch size for bulk write operations
        
    Returns:
        Dict with metrics: {inserted: int, updated: int, rejected: int}
    """
    if not predictions:
        logger.warning("[persist_predictions] No predictions received")
        return {"inserted": 0, "updated": 0, "rejected": 0}
    
    total_inserted = 0
    total_updated = 0
    total_rejected = 0
    chunks_completed = 0
    
    for i in range(0, len(predictions), batch_size):
        batch = predictions[i:i + batch_size]
        operations = []
        
        for doc in batch:
            # Build natural key filter
            filter_doc = {key: doc.get(key) for key in FILTER_KEYS if key in doc}
            
            if len(filter_doc) < len(FILTER_KEYS):
                logger.warning(f"[persist_predictions] Document rejected (missing filter keys): {doc}")
                total_rejected += 1
                continue
            
            operations.append(
                UpdateOne(filter_doc, {"$set": doc}, upsert=True)
            )
        
        if not operations:
            continue
        
        try:
            result = collection.bulk_write(operations, ordered=False)
            total_inserted += result.upserted_count
            total_updated += result.modified_count
            chunks_completed += 1
            
            logger.info(
                f"[persist_predictions] Batch {chunks_completed}: "
                f"Inserted: {result.upserted_count}, Updated: {result.modified_count}"
            )
        except BulkWriteError as e:
            total_rejected += len(e.details.get("writeErrors", []))
            total_inserted += e.details.get("nUpserted", 0)
            total_updated += e.details.get("nUpdated", 0)
            logger.error(f"[persist_predictions] BulkWriteError: {e.details}")
    
    metrics = {
        "inserted": total_inserted,
        "updated": total_updated,
        "rejected": total_rejected,
    }
    
    logger.info(f"[persist_predictions] Final metrics: {metrics}")
    return metrics
