import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from collections.abc import Iterator

from src.etl.extract.extract_energy_losses import extract_losses
from src.etl.extract.extract_decfec import extract_decfec
from src.etl.extract.extract_limits import extract_limits
from src.etl.extract.gdb_orchestrator import run_extraction
from src.etl.transform.contract import TRANSFORM_CONTRACT_VERSION
from src.etl.transform.transform_decfec import transform_decfec
from src.etl.transform.transform_limits import transform_limits
from src.etl.transform.transform_energy_losses import transform_energy_losses

from pymongo.database import Database

from src.repositories.load_history_repository import (
    insert_load_history,
    update_load_history,
    get_load_history
    )

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

TRANSFORMER_MAP = {
    "energy_losses": transform_energy_losses,
    "indicadores_continuidade": transform_decfec,
    "indicadores_continuidade_limite": transform_limits,
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


def _validate_transform_contract(file_key: str, transformed: Any) -> dict[str, Any]:
    if not isinstance(transformed, dict):
        raise ValueError(f"[{file_key}] Transform result must be a dict.")

    required_keys = {"contract_version", "valid", "rejected", "stats"}
    missing = required_keys - set(transformed.keys())
    if missing:
        raise ValueError(f"[{file_key}] Missing transform contract keys: {sorted(missing)}")

    if transformed.get("contract_version") != TRANSFORM_CONTRACT_VERSION:
        raise ValueError(
            f"[{file_key}] Unsupported transform contract version: "
            f"{transformed.get('contract_version')}"
        )

    valid = transformed.get("valid")
    rejected = transformed.get("rejected")
    stats = transformed.get("stats")

    if not isinstance(valid, list) or not isinstance(rejected, list) or not isinstance(stats, dict):
        raise ValueError(f"[{file_key}] Invalid contract field types for valid/rejected/stats.")

    stat_keys = {"total_input", "total_valid", "total_rejected"}
    stat_missing = stat_keys - set(stats.keys())
    if stat_missing:
        raise ValueError(f"[{file_key}] Missing stats keys: {sorted(stat_missing)}")

    total_input = stats.get("total_input")
    total_valid = stats.get("total_valid")
    total_rejected = stats.get("total_rejected")

    if not all(isinstance(v, int) for v in (total_input, total_valid, total_rejected)):
        raise ValueError(f"[{file_key}] Stats values must be integers.")

    if total_input < 0 or total_valid < 0 or total_rejected < 0:
        raise ValueError(f"[{file_key}] Stats values must be >= 0.")

    if total_valid != len(valid) or total_rejected != len(rejected):
        raise ValueError(f"[{file_key}] Stats and payload lengths are inconsistent.")

    if total_valid + total_rejected != total_input:
        raise ValueError(f"[{file_key}] total_input must equal total_valid + total_rejected.")

    return transformed

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
                transformer = TRANSFORMER_MAP.get(file_key)
                if transformer is None:
                    raise ValueError(f"[{file_key}] Missing transformer mapping.")

                result = extractor(path)
                if not isinstance(result, Iterator):
                    raise ValueError(f"[{file_key}] Extractor must return an iterator of chunks.")

                chunks_completed = 0
                total_processed = 0
                total_valid = 0
                total_rejected = 0

                for extracted_chunk in result:
                    chunk_df = extracted_chunk[0] if isinstance(extracted_chunk, tuple) else extracted_chunk
                    chunk_size = len(chunk_df) if hasattr(chunk_df, "__len__") else 0
                    total_processed += chunk_size

                    if chunk_size == 0:
                        continue

                    transformed = transformer(chunk_df)
                    contract = _validate_transform_contract(file_key, transformed)
                    stats = contract["stats"]

                    total_valid += stats["total_valid"]
                    total_rejected += stats["total_rejected"]
                    chunks_completed += 1

                update_load_history(
                    db,
                    load_id,
                    "PROCESSING",
                    {
                        "total_processed": total_processed,
                        "total_inserted": total_valid,
                        "total_rejected": total_rejected,
                        "chunks_completed": chunks_completed,
                    },
                )

                update_load_history(db, load_id, "SUCCESS")
        except Exception as e:
            logger.exception(
                "[upload_service] ETL falhou para file_key='%s', load_id='%s', path='%s'",
                file_key,
                load_id,
                path,
            )
            update_load_history(
                db,
                load_id,
                "ERROR",
                {"error_message": f"[{file_key}] {e.__class__.__name__}: {e}"},
            )

def get_upload_status(db: Database, load_id: str) -> dict | None:
    load_history = get_load_history(db, load_id)
    if not load_history:
        return None
    
    response = {
        "load_id": load_id,
        "status": load_history["status"],
        "metrics": {
            "total_processed": load_history.get("total_processed"),
            "total_valid": load_history.get("total_inserted"),
            "total_rejected": load_history.get("total_rejected"),
            "chunks_completed": load_history.get("chunks_completed"),
        },
    }

    if load_history["status"] == "ERROR":
        response["error_message"] = load_history.get("error_message")
    
    return response