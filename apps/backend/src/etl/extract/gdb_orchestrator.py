import logging
import uuid
from datetime import datetime, timezone
from pymongo.database import Database

from src.etl.extract.gdb_extractor import extract_gdb_generator
from apps.backend.src.etl.transform.transform_gdb import transform_gdb
from src.repositories.load_history_repository import (
    insert_load_history,
    update_load_history
)
from pathlib import Path

logger = logging.getLogger(__name__)

def build_batch(load_id, file_key, source_file, layer_name, df, chunk_index):
    return {
        "load_id": load_id,
        "file_key": file_key,
        "source_file": source_file,
        "layer_name": layer_name,
        "chunk_index": chunk_index,
        "chunk_size": len(df),
        "schema": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "records": df.to_dict(orient="records"),
        "geometry_format": "geojson",
        "extracted_at": datetime.now(timezone.utc)
    }


def build_envelope(batch):
    return {
        "stage": "extraction",
        "parser": "gdb_extractor",
        "parser_version": "1.0",
        "metadata": {},
        "data": batch
    }

def run_extraction(db: Database, path: Path, load_id: str):
    file_key = "gdb_file"
    total_processed = 0
    total_valid = 0
    total_rejected = 0
    chunks_completed = 0

    try:
        # 1. Extração (Gerador)
        for chunk, layer_name, source_file in extract_gdb_generator(path):
            
            if isinstance(chunk, dict): 
                update_load_history(db, load_id, "ERROR", {"error_message": chunk["error"]})
                continue

            # 2. Transformação
            transform_result = transform_gdb(chunk, layer_name, load_id)

            # 3. Log de Rejeições
            if transform_result["rejected"]:
                for rej in transform_result["rejected"]:
                    logger.warning(
                        f"[REJECTED] Layer: {layer_name} | Reason: {rej['reason']}"
                    )

            # 4. Acumulação das Métricas
            stats = transform_result.get("stats", {})
            total_processed += stats.get("total_input", 0)
            total_valid     += stats.get("total_valid", 0)
            total_rejected  += stats.get("total_rejected", 0)
            chunks_completed += 1

            # 5. Log e Update de Progresso (Durante o loop)
            current_metrics = {
                "total_processed": total_processed,
                "total_valid": total_valid,
                "total_rejected": total_rejected,
                "chunks_completed": chunks_completed
            }
            
            update_load_history(db, load_id, "PROCESSING", current_metrics)
            # repository.insert_many(transform_result["valid"])

        # --- FIM DO LOOP ---

        # 6. Montagem das métricas finais (FORA DO LOOP)
        final_metrics = {
            "total_processed": total_processed,
            "total_valid": total_valid,
            "total_rejected": total_rejected,
            "chunks_completed": chunks_completed
        }
        
        logger.info(f"[DONE] Enviando métricas finais: {final_metrics}")

        # 7. Finalização com Sucesso
        update_load_history(db, load_id, "SUCCESS", final_metrics)

    except Exception as e:
        logger.error(f"[FATAL ERROR] Load {load_id}: {str(e)}")
        update_load_history(db, load_id, "ERROR", {"error_message": str(e)})
        raise

def extract_gdb_preview(path: Path) -> list[dict]:
    results = []
    for chunk, layer_name, source_file in extract_gdb_generator(path):
        if isinstance(chunk, dict):
            continue
        df = chunk.drop(columns=["geometry"], errors="ignore")
        results.append({
            "layer_name": layer_name,
            "records": df.to_dict(orient="records")
        })
    return results