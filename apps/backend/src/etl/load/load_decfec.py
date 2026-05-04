import os
import logging
from pymongo.collection import Collection
from pymongo import UpdateOne

from src.config.settings import Settings
from src.control.tam_sam_procedures import Tam_sam_procedures
from src.database.connection import get_client
from src.etl.extract.extract_decfec import extract_decfec
from src.services.retraining_service import schedule_retraining


MANDATORY_FIELDS = [
    "SigAgente", "NumCNPJ", "IdeConjUndConsumidoras",
    "DscConjUndConsumidoras", "SigIndicador", "AnoIndice",
    "NumPeriodoIndice", "VlrIndiceEnviado",
]
MAX_REJECTION_LOGS_PER_CHUNK = 5

settings = Settings()

def _to_str(value) -> str | None:
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return str(value).strip() or None


def _to_float(value) -> float | None:
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return None
        # The CSV stores decimals with comma and may omit the leading zero.
        # Examples: ",44" -> "0.44", "1.234,56" -> "1234.56"
        normalized = normalized.replace(" ", "")
        if "," in normalized:
            normalized = normalized.replace(".", "").replace(",", ".")
        try:
            return float(normalized)
        except (ValueError, TypeError):
            return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _history_totals(totals):
    return {
        "total_processed": totals["rows_processed"],
        "total_inserted": totals["inserted"],
        "total_updated": totals["updated"],
        "total_rejected": totals["rows_rejected"],
        "chunks_completed": totals["chunks_processed"],
    }


def _log_event(event, **payload):
    log_line = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **payload,
    }
    print(json.dumps(log_line, default=str, ensure_ascii=True))

from pymongo.errors import BulkWriteError
from src.etl.utils.bulk_persist import bulk_persist

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 1000

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

    metrics = bulk_persist(collection, docs, FILTER_KEYS)

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
        batch_size = int(os.getenv("ETL_BULK_PERSIST_BATCH_SIZE", DEFAULT_BATCH_SIZE))
        try:
            for i in range(0, len(operations), batch_size):
                batch = operations[i:i + batch_size]
                result = conj_collection.bulk_write(batch, ordered=False)
                logger.info(
                    f"[load_decfec] conj.distribution_indices batch {i//batch_size + 1} — "
                    f"matched: {result.matched_count}, modified: {result.modified_count}"
                )
        except BulkWriteError as e:
            logger.error(f"[load_decfec] BulkWriteError em conj: {e.details}")

    return metrics
