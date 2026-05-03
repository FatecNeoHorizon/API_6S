import logging
from pymongo.collection import Collection
from src.etl.utils.bulk_persist import bulk_persist

logger = logging.getLogger(__name__)

FILTER_KEYS = ["distributor", "process_date"]


def load_energy_losses(transform_result: dict, collection: Collection) -> dict:
    docs = transform_result.get("valid", [])

    clean_docs = [{k: v for k, v in doc.items() if k != "distributor_slug"} for doc in docs]
    
    logger.info(f"[load_energy_losses] Iniciando persist de {len(clean_docs)} documentos.")
    return bulk_persist(collection, clean_docs, FILTER_KEYS)