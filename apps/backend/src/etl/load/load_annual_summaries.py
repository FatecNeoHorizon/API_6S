import logging
from collections import defaultdict

from pymongo import UpdateOne
from pymongo.collection import Collection

logger = logging.getLogger(__name__)

DEFAULT_CRITICALITY_RATIO_NORMAL = 0.8
DEFAULT_CRITICALITY_RATIO_ATTENTION = 1.0


def _classify_criticality(accumulated_value: float, limit: float | None) -> str | None:
    """Classify criticality using the `limit` value stored in an annual_summary.

    Rules:
      - If `limit` is None or not a positive number -> return None
      - Compute `ratio = accumulated_value / limit`
      - `ratio <= DEFAULT_CRITICALITY_RATIO_NORMAL` -> "normal"
      - `DEFAULT_CRITICALITY_RATIO_NORMAL < ratio <= DEFAULT_CRITICALITY_RATIO_ATTENTION` -> "attention"
      - `ratio > DEFAULT_CRITICALITY_RATIO_ATTENTION` -> "critical"

    This implements: "normal / attention above 80% / critical above 100% / null without limit".
    """
    if limit is None:
        return None

    try:
        if float(limit) <= 0:
            return None
    except (TypeError, ValueError):
        return None

    ratio = float(accumulated_value) / float(limit)
    if ratio <= DEFAULT_CRITICALITY_RATIO_NORMAL:
        return "normal"
    if ratio <= DEFAULT_CRITICALITY_RATIO_ATTENTION:
        return "attention"
    return "critical"


def compute_annual_summaries(conj_collection: Collection) -> dict:
    docs = list(
        conj_collection.find(
            {},
            {
                "code": 1,
                "distribution_indices": 1,
                "annual_summaries": 1,
            },
        )
    )

    operations = []
    updated_docs = 0
    updated_summaries = 0

    for doc in docs:
        code = doc.get("code")
        if not code:
            continue

        distribution_totals = defaultdict(lambda: {"accumulated_value": 0.0, "periods_count": 0})
        for entry in doc.get("distribution_indices") or []:
            if not isinstance(entry, dict):
                continue

            indicator_type_code = entry.get("indicator_type_code")
            year = entry.get("year")
            if not indicator_type_code or year is None:
                continue

            key = (indicator_type_code, year)
            totals = distribution_totals[key]
            value = entry.get("value")
            if value is not None:
                try:
                    totals["accumulated_value"] += float(value)
                except (TypeError, ValueError):
                    pass
            totals["periods_count"] += 1

        for summary in doc.get("annual_summaries") or []:
            if not isinstance(summary, dict):
                continue

            indicator_type_code = summary.get("indicator_type_code")
            year = summary.get("year")
            if not indicator_type_code or year is None:
                continue

            key = (indicator_type_code, year)
            if key not in distribution_totals:
                continue

            totals = distribution_totals[key]
            accumulated_value = float(totals["accumulated_value"])
            periods_count = int(totals["periods_count"])
            limit = summary.get("limit")

            operations.append(
                UpdateOne(
                    {
                        "code": code,
                        "annual_summaries": {
                            "$elemMatch": {
                                "indicator_type_code": indicator_type_code,
                                "year": year,
                            }
                        },
                    },
                    {
                        "$set": {
                            "annual_summaries.$.accumulated_value": accumulated_value,
                            "annual_summaries.$.periods_count": periods_count,
                            "annual_summaries.$.status": "complete" if periods_count == 12 else "partial",
                            "annual_summaries.$.criticality": _classify_criticality(accumulated_value, limit),
                        }
                    },
                    upsert=False,
                )
            )

    if operations:
        result = conj_collection.bulk_write(operations, ordered=False)
        updated_docs = result.modified_count
        updated_summaries = len(operations)
        logger.info(
            "[compute_annual_summaries] updated %s summaries across %s documents",
            updated_summaries,
            updated_docs,
        )

    return {
        "updated_documents": updated_docs,
        "updated_summaries": updated_summaries,
    }