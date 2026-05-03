import logging
import threading
from typing import Optional, List, Dict

from src.config.settings import Settings
from src.database.connection import get_client
from src.control.timeseries_forecast_procedures import TimeSeriesForecastProcedures

logger = logging.getLogger(__name__)
settings = Settings()


def retrain_for_load(load_id: str, connection: Optional[object] = None) -> List[Dict]:
    """
    Retrain models for consumer units affected by a specific load_id.

    Returns a list of results for each retrain attempt.
    """
    client = connection or get_client()
    db = client[settings.mongo_db_name]
    collection = db["distribution_indices"]

    cursor = collection.find({"load_id": load_id}, {"consumer_unit_set_id": 1, "indicator_type_code": 1, "year": 1})

    groups = {}
    for doc in cursor:
        cuid = doc.get("consumer_unit_set_id")
        ind = doc.get("indicator_type_code")
        year = doc.get("year")
        if not cuid or not ind:
            continue
        key = (cuid, ind)
        groups.setdefault(key, []).append(year)

    results = []

    procedures = TimeSeriesForecastProcedures(connection=client)

    for (cuid, ind), years in groups.items():
        count = len(years)
        if count < settings.model_retrain_min_new_records:
            logger.info(f"Skipping retrain for {cuid}/{ind}: only {count} new records (min {settings.model_retrain_min_new_records})")
            results.append({"consumer_unit_set_id": cuid, "indicator": ind, "skipped": True, "reason": "not_enough_new_records", "count": count})
            continue

        # Determine a reasonable year range from the newly loaded records
        year_start = min([y for y in years if isinstance(y, int)] or [2015])
        year_end = max([y for y in years if isinstance(y, int)] or [2024])

        logger.info(f"Retraining model for {cuid} {ind} (years {year_start}-{year_end}, {count} records)")
        try:
            res = procedures.forecast_for_unit(
                consumer_unit_set_id=cuid,
                year_start=year_start,
                year_end=year_end,
                indicator_types=[ind],
                save_models=True,
            )
            results.append({"consumer_unit_set_id": cuid, "indicator": ind, "result": res})
        except Exception as exc:
            logger.exception("Retraining failed for %s %s", cuid, ind)
            results.append({"consumer_unit_set_id": cuid, "indicator": ind, "error": str(exc)})

    return results


def schedule_retraining(load_id: str, connection: Optional[object] = None) -> bool:
    """
    Schedule retraining in a background thread and return immediately.
    """
    thread = threading.Thread(target=retrain_for_load, args=(load_id, connection), daemon=True)
    thread.start()
    logger.info("Scheduled retraining for load %s", load_id)
    return True
