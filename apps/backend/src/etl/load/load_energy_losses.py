import logging
from pymongo.collection import Collection
from src.etl.utils.bulk_persist import bulk_persist

logger = logging.getLogger(__name__)

FILTER_KEYS = ["distributor_slug", "process_date"]

def load_energy_losses(transform_result: dict, collection: Collection) -> dict:
    docs = transform_result.get("valid", [])
    logger.info(f"[load_energy_losses] Iniciando persist de {len(docs)} documentos.")
    return bulk_persist(collection, docs, FILTER_KEYS)