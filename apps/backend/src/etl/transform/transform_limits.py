from collections import defaultdict

from src.etl.transform.contract import build_transform_result
from src.etl.transform.utils import (
    _to_str,
    _to_int,
    _to_float,
    _strip_columns
)

REQUIRED = ["code", "indicator_type_code", "year"]

def transform_limits(df):
    df = _strip_columns(df)
    total_input = len(df)

    grouped = defaultdict(list)
    rejected = []

    for _, row in df.iterrows():
        code = _to_str(row.get("IdeConjUndConsumidoras"))
        indicator_type_code = _to_str(row.get("SigIndicador"))
        year = _to_int(row.get("Ano"))
        limit = _to_float(row.get("VlrLimite"))

        if not code or not indicator_type_code or year is None:
            rejected.append({
                "row": row.to_dict(),
                "reason": "Missing required fields"
            })
            continue

        summary = {
            "indicator_type_code": indicator_type_code,
            "year": year,
            "limit": limit
        }

        grouped[code].append(summary)

    documents = [
        {
            "code": code,
            "annual_summaries": summaries
        }
        for code, summaries in grouped.items()
    ]

    return build_transform_result(valid=documents, rejected=rejected, total_input=total_input)