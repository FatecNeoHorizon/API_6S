import logging
import uuid
from datetime import datetime, timezone
from pymongo.database import Database

from src.etl.extract.gdb_extractor import extract_gdb_generator
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
    chunks_completed = 0

    try:
        for chunk, layer_name, source_file in extract_gdb_generator(path):

            if isinstance(chunk, dict):
                update_load_history(
                    db,
                    load_id,
                    "ERROR",
                    {"error_message": chunk["error"]}
                )
                continue

            batch = build_batch(
                load_id,
                file_key,
                source_file,
                layer_name,
                chunk,
                chunks_completed
            )

            envelope = build_envelope(batch)

            # 👉 aqui seria envio (fila, storage, etc)

            total_processed += len(chunk)
            chunks_completed += 1

            update_load_history(
                db,
                load_id,
                "PROCESSING",
                {
                    "total_processed": total_processed,
                    "chunks_completed": chunks_completed
                }
            )

        update_load_history(db, load_id, "SUCCESS")

    except Exception as e:
        update_load_history(
            db,
            load_id,
            "ERROR",
            {"error_message": str(e)}
        )
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