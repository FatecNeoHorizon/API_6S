import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pymongo.database import Database

from src.repositories.load_history_repository import insert_load_history, update_load_history

logger = logging.getLogger(__name__)

COLLECTION_MAP = {
    "energy_losses": "losses",
    "gbd": "gbd",
    "indicadores_continuidade": "distribution_indices",
    "indicadores_continuidade_limite": "conj",
}
 
 
def generate_load_id() -> str:
    return uuid.uuid4().hex

def build_load_document(
        load_id: str,
        file_key: str,
        source_file: str | None = None,
        batch_version: str | None = None
) -> dict:
    return {
        "load_id": load_id,
        "collection_name": COLLECTION_MAP.get(file_key, file_key),
        "batch_version": batch_version or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "source_file": source_file,
        "started_at": datetime.now(timezone.utc),
        "finished_at": None,
        "status": "STARTED",
        "total_processed": None,
        "total_inserted": None,
        "total_updated": None,
        "total_rejected": None,
        "chunks_total": None,
        "chunks_completed": None,
        "error_message": None,
    }

async def register_upload_start(
        db: Database,
        load_id: str,
        path: dict[str, Path],
) -> list[str]:
    
    registered = []

    for file_key, file_path in path.items():
        document = build_load_document(
            load_id=load_id,
            file_key=file_key,
            source_file=str(file_path)
        )
        success = await insert_load_history(db, document)
        if success:
            registered.append(COLLECTION_MAP.get(file_key, file_key))
        else:
            logger.error(f"[upload_service] Falha ao registrar load_history para '{file_key}'")
 
    return registered

async def run_etl_placeholder(
        db: Database,
        load_id: str,
        paths: dict[str, Path],
) -> None:
    
    logger.info(f"[upload_service] ETL iniciado - load_id: {load_id}")
    for file_key, path in paths.items():
        logger.info(f"[upload_service] Pronto para extração: {file_key} → {path}")

    update_load_history(db, load_id, "SUCCESS")
    
    logger.info(f"[upload_service] ETL placeholder concluído — load_id: {load_id}")