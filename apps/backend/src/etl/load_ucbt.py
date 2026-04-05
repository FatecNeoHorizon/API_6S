from datetime import datetime, timezone
from uuid import uuid4

import pandas as pd
from pymongo import MongoClient, UpdateOne

from src.config.parameters import get_mongo_settings, get_mongo_uri
from src.etl.get_ucbt_file import get_ucbt_filepath


MANDATORY_FIELDS = ["COD_ID", "DIST"]


def _normalize_value(value):
    if pd.isna(value):
        return None
    return value


def _normalize_key(value):
    normalized = _normalize_value(value)
    if normalized is None:
        return None
    return str(normalized).strip()


def _history_totals(totals):
    return {
        "total_processed": totals["rows_processed"],
        "total_inserted": totals["inserted"],
        "total_updated": totals["updated"],
        "total_rejected": totals["rows_rejected"],
        "chunks_completed": totals["chunks_processed"],
    }


def load_ucbt_tab(
    file_path: str | None = None,
    chunk_size: int = 100_000,
    batch_version: str | None = None,
    load_id: str | None = None,
):
    source_file = file_path or get_ucbt_filepath()
    if not source_file:
        raise ValueError("UCBT file path is missing. Set UCBT_CSV_FILE_PATH or pass file_path.")

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    batch_version = batch_version or datetime.now(timezone.utc).strftime("v%Y%m%d_%H%M%S")
    load_id = load_id or str(uuid4())

    mongo_uri = get_mongo_uri()
    _, _, _, _, db_name = get_mongo_settings()

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db["ucbt_tab"]
    load_history = db["load_history"]

    started_at = datetime.now(timezone.utc)
    totals = {
        "chunks_processed": 0,
        "rows_processed": 0,
        "rows_valid": 0,
        "rows_rejected": 0,
        "inserted": 0,
        "updated": 0,
        "matched": 0,
    }

    load_history.insert_one(
        {
            "load_id": load_id,
            "collection_name": "ucbt_tab",
            "batch_version": batch_version,
            "source_file": source_file,
            "started_at": started_at,
            "finished_at": None,
            "status": "STARTED",
            "chunks_total": None,
            **_history_totals(totals),
            "error_message": None,
        }
    )

    try:
        chunk_iter = pd.read_csv(
            source_file,
            sep=";",
            encoding="latin-1",
            chunksize=chunk_size,
            low_memory=True,
        )

        for chunk_index, chunk_df in enumerate(chunk_iter, start=1):
            missing_columns = [field for field in MANDATORY_FIELDS if field not in chunk_df.columns]
            if missing_columns:
                raise ValueError(f"Missing mandatory columns in UCBT file: {missing_columns}")

            chunk_rows = len(chunk_df)
            totals["rows_processed"] += chunk_rows

            operations = []
            now = datetime.now(timezone.utc)

            for record in chunk_df.to_dict(orient="records"):
                cod_id = _normalize_key(record.get("COD_ID"))
                dist = _normalize_key(record.get("DIST"))
                if not cod_id or not dist:
                    totals["rows_rejected"] += 1
                    continue

                normalized_doc = {key: _normalize_value(value) for key, value in record.items()}
                normalized_doc["COD_ID"] = cod_id
                normalized_doc["DIST"] = dist
                normalized_doc["batch_version"] = batch_version
                normalized_doc["loaded_at"] = now
                normalized_doc["source_file"] = source_file
                normalized_doc["load_id"] = load_id

                operations.append(
                    UpdateOne(
                        {"COD_ID": cod_id, "DIST": dist},
                        {"$set": normalized_doc},
                        upsert=True,
                    )
                )

            totals["rows_valid"] += len(operations)

            if operations:
                result = collection.bulk_write(operations, ordered=False)
                totals["inserted"] += result.upserted_count
                totals["updated"] += result.modified_count
                totals["matched"] += result.matched_count

            totals["chunks_processed"] += 1
            load_history.update_one(
                {"load_id": load_id},
                {
                    "$set": {
                        "status": "STARTED",
                        **_history_totals(totals),
                        "error_message": None,
                    }
                },
            )
            print(
                "[UCBT] chunk="
                f"{chunk_index} processed={chunk_rows} valid={len(operations)} "
                f"rejected={chunk_rows - len(operations)}"
            )

        finished_at = datetime.now(timezone.utc)
        final_status = "PARTIAL" if totals["rows_rejected"] > 0 else "SUCCESS"
        load_history.update_one(
            {"load_id": load_id},
            {
                "$set": {
                    "status": final_status,
                    "finished_at": finished_at,
                    **_history_totals(totals),
                    "error_message": None,
                }
            },
        )
    except Exception as exc:
        finished_at = datetime.now(timezone.utc)
        load_history.update_one(
            {"load_id": load_id},
            {
                "$set": {
                    "status": "ERROR",
                    "finished_at": finished_at,
                    **_history_totals(totals),
                    "error_message": str(exc),
                }
            },
        )
        raise
    finally:
        client.close()

    return {
        "collection": "ucbt_tab",
        "batch_version": batch_version,
        "load_id": load_id,
        "source_file": source_file,
        "chunk_size": chunk_size,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        **totals,
    }


if __name__ == "__main__":
    load_ucbt_tab()