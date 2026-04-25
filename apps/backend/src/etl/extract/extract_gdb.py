import geopandas as gpd
import logging
import os
from pathlib import Path
from src.utils.find_uploaded_file import find_file_full_path

import uuid
from datetime import datetime, timezone
from pymongo.database import Database

from src.repositories.load_history_repository import (
    insert_load_history,
    update_load_history
)

logger = logging.getLogger(__name__)

def get_gdb_path() -> Path:
    file_name = os.getenv("GDB_FILE_PATH")
    search_folder = os.getenv("TMP_UPLOAD_PATH")
    path_value = find_file_full_path(file_name, search_folder)
    if not path_value:
        raise ValueError("GDB_FILE_PATH environment variable is not set.")
    return Path(path_value)


def extract_layer(path: Path, layer_name: str, limit: int = 10) -> list[dict]:
    gdf = gpd.read_file(path, layer=layer_name)
    
    try:
        if gdf.crs is None:
            raise ValueError(f"Layer {layer_name} sem CRS definido")

        if gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)

    except Exception as e:
        logger.error(f"Erro ao processar CRS da layer {layer_name}: {str(e)}")

    
    gdf = gdf.drop(columns=["geometry"], errors="ignore")
    
    return gdf.to_dict(orient="records")[:limit]


def extract_gdb(db: Database) -> dict:
    load_id = str(uuid.uuid4())

    insert_load_history(db, {
        "load_id": load_id,
        "status": "STARTED",
        "started_at": datetime.now(timezone.utc),
        "collection_name": "gdb_extraction",
        "batch_version": "1.0",
        "total_processed": 0,
        "chunks_completed": 0
    })

    try:
        path = get_gdb_path()
        layers = gpd.list_layers(path)["name"].tolist()

        targets = {
            "CONJ":   10,
            "SUB":    10,
            "UNTRMT": 10,
            "UNTRAT": 10,
        }

        result = {}
        total_processed = 0
        chunks_completed = 0

        for layer_name, limit in targets.items():
            if layer_name in layers:
                data = extract_layer(path, layer_name, limit=limit)
                result[layer_name] = data

                total_processed += len(data)
                chunks_completed += 1

                # 🔄 atualização incremental
                update_load_history(
                    db,
                    load_id,
                    status="PROCESSING",
                    extra_fields={
                        "total_processed": total_processed,
                        "chunks_completed": chunks_completed
                    }
                )
            else:
                result[layer_name] = []

        # ✅ finalização
        update_load_history(
            db,
            load_id,
            status="SUCCESS",
            extra_fields={
                "total_processed": total_processed,
                "chunks_completed": chunks_completed
            }
        )

        # 👇 mantém seu retorno atual + load_id (útil pra rastrear)
        return {
            "load_id": load_id,
            "data": result
        }

    except Exception as e:
        update_load_history(
            db,
            load_id,
            status="ERROR",
            extra_fields={
                "error_message": str(e)
            }
        )
        raise