import logging
from pymongo.collection import Collection
from src.etl.utils.bulk_persist import bulk_persist

logger = logging.getLogger(__name__)

FILTER_KEYS_CONJ = ["code"]
FILTER_KEYS_SUB  = ["code"]
FILTER_KEYS_TRANSFORMERS = ["code"]

def load_conj(transform_result: dict, collection: Collection) -> dict:
    docs = [d for d in transform_result.get("valid", []) if d.get("layer_source") == "CONJ"]
    logger.info(f"[load_conj] Iniciando persistência de {len(docs)} documentos.")
    return bulk_persist(collection, docs, FILTER_KEYS_CONJ)

def load_sub(transform_result: dict, collection: Collection) -> dict:
    docs = [d for d in transform_result.get("valid", []) if d.get("layer_source") == "SUB"]
    logger.info(f"[load_sub] Iniciando persistência de {len(docs)} documentos.")
    return bulk_persist(collection, docs, FILTER_KEYS_SUB)

def load_transformers(transform_result: dict, collection: Collection) -> dict:
    docs = [d for d in transform_result.get("valid", []) if d.get("layer_source") == "UN_TRA_D"]
    logger.info(f"[load_transformers] Iniciando persistência de {len(docs)} documentos.")
    return bulk_persist(collection, docs, FILTER_KEYS_TRANSFORMERS)