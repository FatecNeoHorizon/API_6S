import logging
import uuid
from bson import ObjectId
from datetime import datetime, timezone
from pymongo.database import Database

from src.etl.extract.gdb_extractor import extract_gdb_generator
from src.etl.transform.transform_gdb import transform_gdb
from src.etl.load.load_gdb import load_conj
from src.etl.load.load_gdb import load_conj, load_sub, load_transformers

from src.repositories.load_history_repository import (
    update_load_history
)
from pathlib import Path

logger = logging.getLogger(__name__)

def build_batch(load_id, file_key, source_file, layer_name, df, chunk_index):
    """
    Construir um lote de dados extraídos do GDB.
    
    Agrupa informações sobre o carregamento, dados e metadados em um único dicionário
    que será processado posteriormente nas etapas de transformação e carga.
    """
    return {
        "load_id": load_id,                                                      # ID único do carregamento
        "file_key": file_key,                                                    # Chave/tipo do arquivo
        "source_file": source_file,                                              # Caminho do arquivo original
        "layer_name": layer_name,                                                # Nome da layer geográfica
        "chunk_index": chunk_index,                                              # Índice sequencial do lote
        "chunk_size": len(df),                                                   # Quantidade de registros
        "schema": {col: str(dtype) for col, dtype in df.dtypes.items()},        # Tipos de dados das colunas
        "records": df.to_dict(orient="records"),                                 # Dados convertidos para lista de dicts
        "geometry_format": "geojson",                                            # Formato dos dados geométricos
        "extracted_at": datetime.now(timezone.utc)                               # Timestamp da extração
    }


def build_envelope(batch):
    """
    Envolver o lote em um envelope com metadados de processamento.
    
    Adiciona informações sobre o estágio, parser e versão para rastreabilidade
    e auditoria durante todo o pipeline ETL.
    """
    return {
        "stage": "extraction",                     # Etapa do pipeline (extração)
        "parser": "gdb_extractor",                 # Tipo de parser utilizado
        "parser_version": "1.0",                   # Versão do parser
        "metadata": {},                            # Metadados adicionais (flexível)
        "data": batch                              # Dados do lote preparado
    }

def run_extraction(db: Database, path: Path, load_id: str):
    file_key = "gdb_file"
    total_processed = 0
    total_valid = 0
    total_rejected = 0
    chunks_completed = 0

    try:
        # 1. Registra o GDB no banco e obtém o geodatabase_id
        geodatabase_doc = {
            "filename": Path(path).name,
            "load_id": load_id,
            "uploaded_at": datetime.now(timezone.utc),
            "distributor": None,
            "reference_year": None,
        }
        geodatabase_id = str(db["geodatabases"].insert_one(geodatabase_doc).inserted_id)
    
        # 2. Extração (Gerador)
        for chunk, layer_name, source_file in extract_gdb_generator(path):
            
            if isinstance(chunk, dict):
                update_load_history(db, load_id, "ERROR", {"error_message": chunk["error"]})
                continue

            # 3. Transformação
            transform_result = transform_gdb(chunk, layer_name, geodatabase_id)

            if transform_result["rejected"]:
                for rej in transform_result["rejected"]:
                    logger.warning(
                        f"[REJECTED] Layer: {layer_name} | Reason: {rej['reason']}"
                    )

            valid_docs = transform_result.get("valid", [])

            if layer_name == "CONJ":
                load_metrics = load_conj(transform_result, db["conj"])
            elif layer_name == "SUB":
                load_metrics = load_sub(transform_result, db["substations"])
            elif layer_name == "UN_TRA_D":
                load_metrics = load_transformers(transform_result, db["distribution_transformers"])

            stats = transform_result.get("stats", {})
            total_processed += stats.get("total_input", 0)
            total_valid     += stats.get("total_valid", 0)
            total_rejected  += stats.get("total_rejected", 0)
            chunks_completed += 1

            current_metrics = {
                "total_processed": total_processed,
                "total_valid": total_valid,
                "total_rejected": total_rejected,
                "chunks_completed": chunks_completed
            }

            update_load_history(db, load_id, "PROCESSING", current_metrics)
            
        final_metrics = {
            "total_processed": total_processed,
            "total_valid": total_valid,
            "total_rejected": total_rejected,
            "chunks_completed": chunks_completed
        }

        logger.info(f"[DONE] Enviando métricas finais: {final_metrics}")
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