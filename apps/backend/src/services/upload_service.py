import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from src.etl.extract.extract_energy_losses import extract_losses
from src.etl.extract.extract_decfec import extract_decfec
from src.etl.extract.extract_limits import extract_limits
from src.etl.extract.gdb_orchestrator import run_extraction

from pymongo.database import Database

from src.repositories.load_history_repository import (
    insert_load_history,
    update_load_history,
    get_load_history
    )

from src.control.upload_procedures import cleanup_upload_dir

logger = logging.getLogger(__name__)

COLLECTION_MAP = {
    "energy_losses": "losses",
    "gdb": "gdb",
    "indicadores_continuidade": "distribution_indices",
    "indicadores_continuidade_limite": "conj",
    }

EXTRACTOR_MAP = {
    "energy_losses":                extract_losses,
    "gdb":                          run_extraction,
    "indicadores_continuidade":     extract_decfec,
    "indicadores_continuidade_limite": extract_limits,
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

def register_upload_start(
        db: Database,
        paths: dict[str, Path],
    ) -> dict[str, str]:
    registered = {}
    for file_key, file_path in paths.items():
        load_id = generate_load_id()
        document = build_load_document(
            load_id=load_id,
            file_key=file_key,
            source_file=str(file_path)
        )
        success = insert_load_history(db, document)
        if success:
            registered[file_key] = load_id
        else:
            logger.error(f"[upload_service] Falha ao registrar load_history para '{file_key}'")
    return registered

def run_etl(db, load_ids, paths, upload_dir):
    for file_key, path in paths.items():
        load_id = load_ids.get(file_key)
        extractor = EXTRACTOR_MAP.get(file_key)
        if not extractor:
            continue
        try:
            update_load_history(db, load_id, "PROCESSING")
            if file_key == "gdb":
                extractor(db, path, load_id)
            else:
                result = extractor(path)
                update_load_history(db, load_id, "SUCCESS")
        except Exception as e:
            update_load_history(db, load_id, "ERROR", {"error_message": str(e)})

def get_upload_status(db: Database, load_id: str) -> dict | None:
    load_history = get_load_history(db, load_id)
    if not load_history:
        return None
    
    response = {
        "load_id": load_id,
        "status": load_history["status"],
    }

    if load_history["status"] == "ERROR":
        response["error_message"] = load_history.get("error_message")
    
    return response