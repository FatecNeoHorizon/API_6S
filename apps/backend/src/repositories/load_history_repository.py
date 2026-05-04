import logging
from datetime import datetime, timezone

from pymongo.database import Database
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

COLLECTION_NAME = "load_history"

def insert_load_history(db: Database, document: dict) -> bool:
    try:
        db[COLLECTION_NAME].insert_one(document)
        logger.info(f"[load_history_repository] Inserido load_id: {document.get('load_id')}")
        return True
    except PyMongoError as e:
        logger.error(f"[load_history_repository] Erro ao inserir load history: {e}")
        return False
    
def update_load_history(
    db: Database, 
    load_id: str,
    status: str,
    extra_fields: dict | None = None
) -> bool:
    
    update_data = {
        "status": status,
        "finished_at": datetime.now(timezone.utc)
    }

    ROOT_FIELDS = {"reconciliation"}

    if status == "SUCCESS" or status == "ERROR":
        update_data["finished_at"] = datetime.now(timezone.utc)

    if extra_fields:
        for key, value in extra_fields.items():
            if key in ROOT_FIELDS:
                update_data[key] = value
            else:
                update_data[f"metrics.{key}"] = value

    update = {"$set": update_data}

    try:
        # 1. Capture o objeto de resultado do PyMongo
        mongo_result = db[COLLECTION_NAME].update_one({"load_id": load_id}, update)
        
        # 2. Verifique se algum documento foi encontrado (matched_count)
        if mongo_result.matched_count == 0:
            logger.warning(f"[load_history_repository] load_id não encontrado: {load_id}")
            return False
            
        logger.info(f"[load_history_repository] load_id {load_id} atualizado para {status}")
        return True
        
    except PyMongoError as e:
        logger.error(f"[load_history_repository] Erro ao atualizar: {e}")
        return False

def get_load_history(db: Database, load_id: str) -> dict | None:
    return db[COLLECTION_NAME].find_one({"load_id": load_id})

def get_load_history_by_batch(db: Database, batch_id: str) -> list[dict]:
    return list(db[COLLECTION_NAME].find({"batch_id": batch_id}))