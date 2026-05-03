import logging
import pandas as pd
from src.etl.utils.contract import build_transform_result, TRANSFORM_CONTRACT_VERSION
from src.etl.utils.transform_functions import _to_str, _to_float, _to_int, _to_date

logger = logging.getLogger(__name__)

def transform_decfec(df: pd.DataFrame):
    df_work = df.copy(deep=True)
    total_input = len(df_work)

    valid_docs = []
    rejected_docs = []

    for _, row in df_work.iterrows():
        try:
            row_dict = row.to_dict()

            agent_acronym              = _to_str(row.get("SigAgente"))
            cnpj_number                = _to_str(row.get("NumCNPJ"))
            consumer_unit_set_id       = _to_str(row.get("IdeConjUndConsumidoras"))
            consumer_unit_set_description = _to_str(row.get("DscConjUndConsumidoras"))
            indicator_type_code        = _to_str(row.get("SigIndicador"))
            year                       = _to_int(row.get("AnoIndice"))
            period                     = _to_int(row.get("NumPeriodoIndice"))
            
            valor_str = str(row.get("VlrIndiceEnviado") or "").strip().replace(",", ".")
            valor     = pd.to_numeric(valor_str, errors="coerce")

            if not agent_acronym or not cnpj_number or not consumer_unit_set_id \
                    or not consumer_unit_set_description or not indicator_type_code \
                    or year is None or period is None:
                rejected_docs.append({
                    "row": row_dict,
                    "reason": "Missing required fields"
                })
                continue

            valid_docs.append({
                "agent_acronym":               agent_acronym,
                "cnpj_number":                 cnpj_number,
                "consumer_unit_set_id":        consumer_unit_set_id,
                "consumer_unit_set_description": consumer_unit_set_description,
                "indicator_type_code":         indicator_type_code,
                "year":                        year,
                "period":                      period,
                "value": float(valor) if not pd.isna(valor) else None,
            })

        except Exception as e:
            logger.error(f"Error processing row: {str(e)}")
            rejected_docs.append({"row": row.to_dict(), "reason": f"Exception: {str(e)}"})

            
    result = build_transform_result(valid_docs, rejected_docs, total_input)
    result["contract_version"] = TRANSFORM_CONTRACT_VERSION
    logger.info(f"Transformer completo: {len(valid_docs)} validos, {len(rejected_docs)} rejeitados, do {total_input} total")
    return result