from datetime import datetime, timezone
from src.etl.get_decfec_file import get_filepath
from uuid import uuid4
import json
import time

import pandas as pd
from pymongo import MongoClient, UpdateOne

from src.config.parameters import get_mongo_settings, get_mongo_uri
from src.etl.extract.extract_decfec import extract_decfec


MANDATORY_FIELDS = [
    "SigAgente", "NumCNPJ", "IdeConjUndConsumidoras",
    "DscConjUndConsumidoras", "SigIndicador", "AnoIndice",
    "NumPeriodoIndice", "VlrIndiceEnviado",
]
MAX_REJECTION_LOGS_PER_CHUNK = 5


def _to_str(value) -> str | None:
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return str(value).strip() or None


def _to_float(value) -> float | None:
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _history_totals(totals):
    return {
        "total_processed": totals["rows_processed"],
        "total_inserted": totals["inserted"],
        "total_updated": totals["updated"],
        "total_rejected": totals["rows_rejected"],
        "chunks_completed": totals["chunks_processed"],
    }


def _log_event(event, **payload):
    log_line = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **payload,
    }
    print(json.dumps(log_line, default=str, ensure_ascii=True))


def load_decfec(
    batch_version: str | None = None,
    load_id: str | None = None,
):

    batch_version = batch_version or datetime.now(timezone.utc).strftime("v%Y%m%d_%H%M%S")
    load_id = load_id or str(uuid4())

    mongo_uri = get_mongo_uri()
    _, _, _, _, db_name = get_mongo_settings()

    client = MongoClient(
        mongo_uri,
        serverSelectionTimeoutMS=120000,
        socketTimeoutMS=120000,
    )
    db = client[db_name]
    collection = db["distribution_indices"]
    load_history = db["load_history"]

    started_at = datetime.now(timezone.utc)
    start_perf = time.perf_counter()

    totals = {
        "chunks_processed": 0,
        "rows_processed": 0,
        "rows_valid": 0,
        "rows_rejected": 0,
        "inserted": 0,
        "updated": 0,
        "matched": 0,
    }

    source_file = get_filepath()


    load_history.insert_one({
        "load_id": load_id,
        "collection_name": "distribution_indices",
        "batch_version": batch_version,
        "source_file": source_file,
        "started_at": started_at,
        "finished_at": None,
        "status": "STARTED",
        "chunks_total": None,
        **_history_totals(totals),
        "error_message": None,
    })

    _log_event(
        "decfec_load_started",
        load_id=load_id,
        batch_version=batch_version,
        source_file=source_file,
    )

    try:
        for chunk_index, (chunk_df, source_file) in enumerate(extract_decfec(), start=1):
            chunk_start_perf = time.perf_counter()
            chunk_rows = len(chunk_df)
            totals["rows_processed"] += chunk_rows

            operations = []
            now = datetime.now(timezone.utc)
            rejected_samples = []

            for row_in_chunk, record in enumerate(chunk_df.to_dict(orient="records"), start=1):
                agent_acronym        = _to_str(record.get("SigAgente"))
                consumer_unit_set_id = _to_str(record.get("IdeConjUndConsumidoras"))
                indicator_type_code  = _to_str(record.get("SigIndicador"))
                year                 = record.get("AnoIndice")
                period               = record.get("NumPeriodoIndice")

                missing = []
                if not agent_acronym:        missing.append("agent_acronym")
                if not consumer_unit_set_id: missing.append("consumer_unit_set_id")
                if not indicator_type_code:  missing.append("indicator_type_code")
                if not year:                 missing.append("year")
                if not period:               missing.append("period")

                if missing:
                    totals["rows_rejected"] += 1
                    if len(rejected_samples) < MAX_REJECTION_LOGS_PER_CHUNK:
                        rejected_samples.append({
                            "row_in_chunk": row_in_chunk,
                            "reason": f"missing_{'_'.join(missing)}",
                        })
                    continue

                doc = {
                    "agent_acronym":                agent_acronym,
                    "cnpj_number":                  _to_str(record.get("NumCNPJ")),
                    "consumer_unit_set_id":          consumer_unit_set_id,
                    "consumer_unit_set_description": _to_str(record.get("DscConjUndConsumidoras")),
                    "indicator_type_code":           indicator_type_code,
                    "year":                          int(year),
                    "period":                        int(period),
                    "value":                         _to_float(record.get("VlrIndiceEnviado")),
                    "generation_date":               _to_str(record.get("DatGeracaoConjuntoDados")),
                    "batch_version":                 batch_version,
                    "loaded_at":                     now,
                    "source_file":                   source_file,
                    "load_id":                       load_id,
                }

                filter_key = {
                    "agent_acronym":        agent_acronym,
                    "consumer_unit_set_id": consumer_unit_set_id,
                    "indicator_type_code":  indicator_type_code,
                    "year":                 int(year),
                    "period":               int(period),
                }

                operations.append(UpdateOne(filter_key, {"$set": doc}, upsert=True))

            totals["rows_valid"] += len(operations)

            if operations:
                result = collection.bulk_write(operations, ordered=False)
                totals["inserted"] += result.upserted_count
                totals["updated"]  += result.modified_count
                totals["matched"]  += result.matched_count

            totals["chunks_processed"] += 1

            load_history.update_one(
                {"load_id": load_id},
                {"$set": {"status": "STARTED", **_history_totals(totals), "error_message": None}},
            )

            chunk_duration_ms = round((time.perf_counter() - chunk_start_perf) * 1000, 2)
            _log_event(
                "decfec_chunk_summary",
                load_id=load_id,
                batch_version=batch_version,
                chunk_index=chunk_index,
                rows_processed=chunk_rows,
                rows_valid=len(operations),
                rows_rejected=chunk_rows - len(operations),
                inserted=totals["inserted"],
                updated=totals["updated"],
                duration_ms=chunk_duration_ms,
            )

            if rejected_samples:
                _log_event(
                    "decfec_chunk_rejections",
                    load_id=load_id,
                    batch_version=batch_version,
                    chunk_index=chunk_index,
                    sample_size=len(rejected_samples),
                    samples=rejected_samples,
                )

        finished_at = datetime.now(timezone.utc)
        final_status = "PARTIAL" if totals["rows_rejected"] > 0 else "SUCCESS"

        load_history.update_one(
            {"load_id": load_id},
            {"$set": {
                "status": final_status,
                "finished_at": finished_at,
                **_history_totals(totals),
                "error_message": None,
            }},
        )
        _log_event(
            "decfec_load_finished",
            load_id=load_id,
            batch_version=batch_version,
            status=final_status,
            duration_ms=round((time.perf_counter() - start_perf) * 1000, 2),
            totals=totals,
        )

    except Exception as exc:
        finished_at = datetime.now(timezone.utc)
        load_history.update_one(
            {"load_id": load_id},
            {"$set": {
                "status": "ERROR",
                "finished_at": finished_at,
                **_history_totals(totals),
                "error_message": str(exc),
            }},
        )
        _log_event(
            "decfec_load_failed",
            load_id=load_id,
            batch_version=batch_version,
            error=str(exc),
            duration_ms=round((time.perf_counter() - start_perf) * 1000, 2),
            totals=totals,
        )
        raise

    finally:
        client.close()

    return {
        "collection": "distribution_indices",
        "batch_version": batch_version,
        "load_id": load_id,
        "source_file": source_file,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        **totals,
    }


if __name__ == "__main__":
    load_decfec()