import logging
from pymongo.database import Database

logger = logging.getLogger(__name__)

RECONCILIATION_CHECKS = {
    "indicadores_continuidade": ["indicadores_conjunto"],
}

def _check_indicadores_conjunto(db: Database) -> dict:
    pipeline = [
        {"$group": {"_id": "$consumer_unit_set_id"}},
    ]
    set_ids = [
        doc["_id"]
        for doc in db["distribution_indices"].aggregate(pipeline)
        if doc["_id"]
    ]

    checked = len(set_ids)
    if checked == 0:
        return {"checked": 0, "valid": 0, "invalid": 0}

    existing_codes = set(
        doc["code"]
        for doc in db["conj"].find(
            {"code": {"$in": set_ids}},
            {"code": 1, "_id": 0}
        )
    )

    valid   = sum(1 for sid in set_ids if sid in existing_codes)
    invalid = checked - valid

    return {"checked": checked, "valid": valid, "invalid": invalid}


CHECKS_MAP = {
    "indicadores_conjunto": _check_indicadores_conjunto,
}


def run_reconciliation(db: Database, file_key: str, load_id: str) -> dict:
    checks_to_run = RECONCILIATION_CHECKS.get(file_key, [])

    if not checks_to_run:
        logger.info(f"[reconcile] Nenhuma checagem definida para '{file_key}'.")
        return {}

    results = {}
    has_warnings = False

    for check_name in checks_to_run:
        check_fn = CHECKS_MAP.get(check_name)
        if not check_fn:
            logger.warning(f"[reconcile] Checagem '{check_name}' não encontrada.")
            continue

        result = check_fn(db)
        results[check_name] = result

        if result.get("invalid", 0) > 0:
            has_warnings = True

        logger.info(f"[reconcile] '{check_name}' — {result}")

    reconciliation = {
        "status":  "WARNING" if has_warnings else "OK",
        "results": results,
    }

    return reconciliation