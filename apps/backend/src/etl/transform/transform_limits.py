import logging
from src.etl.utils.contract import build_transform_result, TRANSFORM_CONTRACT_VERSION
from src.etl.utils.transform_functions import (
    _to_str,
    _to_int,
    _to_float,
    _strip_columns
)

logger = logging.getLogger(__name__)

def transform_limits(df) -> dict:
    df = _strip_columns(df)
    total_input = len(df)
    
    valid_docs = []
    rejected_docs = []


    for _, row in df.iterrows():
        try:
            code = _to_str(row.get("IdeConjUndConsumidoras"))
            indicator_type_code = _to_str(row.get("SigIndicador"))
            year = _to_int(row.get("AnoLimiteQualidade"))
            limit = _to_float(row.get("VlrLimite"))

            if not code or not indicator_type_code or year is None or limit is None:
                rejected_docs.append({
                    "row": row.to_dict(),
                    "reason": "Missing required fields (code, indicator, year or limit)"
                })
                continue

            valid_docs.append({
                "code": code,
                "indicator_type_code": indicator_type_code,
                "year": year,
                "limit": limit
            })

        except Exception as e:
            logger.error(f"Erro no processamento da linha: {str(e)}")
            rejected_docs.append({
                "row": row.to_dict(),
                "reason": f"Exception: {str(e)}"
            })

    result = build_transform_result(valid_docs, rejected_docs, total_input)
    result["contract_version"] = TRANSFORM_CONTRACT_VERSION
    logger.info(f"Transformer completo: {len(valid_docs)} válidos, {len(rejected_docs)} rejeitados, do {total_input} total")
    return result