import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from collections.abc import Iterator

from src.etl.utils.contract import TRANSFORM_CONTRACT_VERSION

from src.etl.reconcile.reconcile import run_reconciliation

# Importação dos extratores
from src.etl.extract.extract_energy_losses import extract_losses
from src.etl.extract.extract_decfec import extract_decfec
from src.etl.extract.extract_limits import extract_limits
from src.etl.extract.gdb_orchestrator import run_extraction

# Importação dos transformadores
from src.etl.transform.transform_decfec import transform_decfec
from src.etl.transform.transform_limits import transform_limits
from src.etl.transform.transform_energy_losses import transform_energy_losses
from src.repositories.load_history_repository import (
    insert_load_history,
    update_load_history,
    get_load_history,
    get_load_history_by_batch,
)

# Importação dos carregadores
from src.etl.load.load_energy_losses import load_energy_losses
from src.etl.load.load_decfec import load_decfec
from src.etl.load.load_limits import load_limits


from pymongo.database import Database

from src.repositories.load_history_repository import (
    insert_load_history,
    update_load_history,
    get_load_history
    )

logger = logging.getLogger(__name__)

COLLECTION_MAP = {
    "energy_losses": "energy_losses_tariff",
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

LOAD_MAP = {
    "energy_losses": load_energy_losses,
    "indicadores_continuidade": load_decfec,
    "indicadores_continuidade_limite": load_limits,
}

PROCESSING_ORDER = [
    "gdb",
    "energy_losses",
    "indicadores_continuidade_limite",
    "indicadores_continuidade",
]



def generate_load_id() -> str:
    return uuid.uuid4().hex

def build_load_document(
        load_id: str,
        file_key: str,
        source_file: str | None = None,
        batch_version: str | None = None,
        batch_id: str | None = None,
    ) -> dict:
    return {
        "load_id": load_id,
        "batch_id": batch_id,                                          # ← novo
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
        batch_id: str,
    ) -> dict[str, str]:
    registered = {}
    for file_key, file_path in paths.items():
        load_id = generate_load_id()
        document = build_load_document(
            load_id=load_id,
            file_key=file_key,
            source_file=str(file_path),
            batch_id=batch_id,
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

import shutil

def run_etl(db, load_ids, paths, upload_dir):

    ordered_keys = [k for k in PROCESSING_ORDER if k in paths]
    remaining = [k for k in paths if k not in PROCESSING_ORDER]
    ordered_paths = {k: paths[k] for k in ordered_keys + remaining}

    for file_key, path in ordered_paths.items():
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
                    raise ValueError(f"[{file_key}] Mapeamento de transformador ausente.")

                load = LOAD_MAP.get(file_key)
                if load is None:
                    raise ValueError(f"[{file_key}] Mapeamento de carregador ausente.")
                
                result = extractor(path)
                if not isinstance(result, Iterator):
                    raise ValueError(f"[{file_key}] O extrator deve retornar um iterador de chunks.")
                
                total_processed = 0
                total_valid = 0
                total_inserted = 0
                total_rejected = 0
                total_updated = 0   
                chunks_completed = 0

                collection_name = COLLECTION_MAP.get(file_key)

                for extracted_chunk in result:
                    chunk_df = extracted_chunk[0] if isinstance(extracted_chunk, tuple) else extracted_chunk
                    chunk_size = len(chunk_df) if hasattr(chunk_df, "__len__") else 0
                    total_processed += chunk_size

                    if chunk_size == 0:
                        continue

                    transformed = transformer(chunk_df)
                    contract = _validate_transform_contract(file_key, transformed)
                    stats = contract["stats"]

                    if file_key == "indicadores_continuidade":
                        load_metrics = load(contract, db[collection_name], db["conj"])
                    elif file_key == "indicadores_continuidade_limite":
                        load_metrics = load(contract, db["conj"])
                    else:
                        load_metrics = load(contract, db[collection_name])

                    total_valid += stats["total_valid"]
                    total_inserted += load_metrics["inserted"]
                    total_updated  += load_metrics["updated"]
                    total_rejected += stats["total_rejected"]
                    chunks_completed += 1

                update_load_history(
                    db,
                    load_id,
                    "PROCESSING",
                    {
                        "total_processed": total_processed,
                        "total_valid": total_valid,
                        "total_inserted": total_inserted,
                        "total_updated": total_updated,
                        "total_rejected": total_rejected,
                        "chunks_completed": chunks_completed,
                    },
                )

                reconciliation = run_reconciliation(db, file_key, load_id)

                final_status = "SUCCESS"
                if reconciliation.get("status") == "WARNING":
                    final_status = "SUCCESS_WITH_WARNINGS"

                update_load_history(
                    db,
                    load_id,
                    final_status,
                    {"reconciliation": reconciliation} if reconciliation else None,
                )

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

    # Limpeza da pasta temporária após o processamento de todos os arquivos
    try:
        upload_path = Path(upload_dir)
        if upload_path.exists():
            shutil.rmtree(upload_path)
            logger.info(f"[run_etl] Pasta temporária removida: {upload_dir}")
    except Exception as e:
        logger.warning(f"[run_etl] Falha ao remover pasta temporária '{upload_dir}': {e}")
        
def get_upload_status(db: Database, load_id: str) -> dict | None:
    load_history = get_load_history(db, load_id)
    
    if not load_history:
        logger.warning(f"[FETCH_STATUS] Nenhum registro encontrado para o load_id: {load_id}")
        return None
    
    logger.info(f"[FETCH_STATUS] Documento bruto do banco: {load_history}")
    
    db_metrics = load_history.get("metrics", {})
    if not isinstance(db_metrics, dict):
        db_metrics = {}

    # --- LÓGICA DE CAPTURA DE ERRO ---
    # Busca na raiz OU dentro de metrics (onde o novo repositório grava)
    error_msg = load_history.get("error_message") or db_metrics.get("error_message")

    response = {
        "load_id": load_id,
        "status": load_history.get("status"),
        "metrics": {
            "total_processed": db_metrics.get("total_processed") or load_history.get("total_processed"),
            "total_valid": db_metrics.get("total_valid") or load_history.get("total_valid"),
            "total_rejected": (
                db_metrics["total_rejected"]
                if "total_rejected" in db_metrics
                else load_history.get("total_rejected")
            ),
            "chunks_completed": db_metrics.get("chunks_completed") or load_history.get("chunks_completed"),
        },
        "reconciliation": load_history.get("reconciliation"),  # ← adicionar
    }

    logger.info(f"[FETCH_STATUS] Resposta final montada: {response}")
    return response

def get_batch_status(db: Database, batch_id: str) -> dict | None:
    records = get_load_history_by_batch(db, batch_id)

    if not records:
        return None

    PRIORITY = ["ERROR", "PROCESSING", "STARTED", "SUCCESS_WITH_WARNINGS", "SUCCESS"]

    files = {}
    statuses = []

    for record in records:
        file_key = record.get("collection_name")
        status = record.get("status")
        statuses.append(status)

        db_metrics = record.get("metrics", {}) or {}

        files[file_key] = {
            "load_id":   record.get("load_id"),
            "status":    status,
            "metrics": {
                "total_processed":  db_metrics.get("total_processed"),
                "total_valid":      db_metrics.get("total_valid"),
                "total_inserted":   db_metrics.get("total_inserted"),
                "total_updated":    db_metrics.get("total_updated"),
                "total_rejected":   db_metrics.get("total_rejected"),
                "chunks_completed": db_metrics.get("chunks_completed"),
            },
            "reconciliation": record.get("reconciliation"),
        }

    # Status do batch = o mais crítico entre os arquivos
    batch_status = next(
        (s for s in PRIORITY if s in statuses),
        "STARTED"
    )

    return {
        "batch_id":   batch_id,
        "status":     batch_status,
        "files":      files,
    }
