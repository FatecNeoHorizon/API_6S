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
    
    update = {
        "$set":{
            "status": status,
            "finished_at": datetime.now(timezone.utc),
            **(extra_fields or {}),
        }
    }

    try:
        result = db[COLLECTION_NAME].update_one({"load_id": load_id}, update)
        if result.matched_count == 0:
            logger.warning(f"[load_history_repository] load_id não encontrado: {load_id}")
            return False
        logger.info(f"[load_history_repository] load_id {load_id} atualizado para {status}")
        return True
    except PyMongoError as e:
        logger.error(f"[load_history_repository] Erro ao atualizar: {e}")
        return False

def get_load_history(db: Database, load_id: str) -> dict | None:
    return db[COLLECTION_NAME].find_one({"load_id": load_id})