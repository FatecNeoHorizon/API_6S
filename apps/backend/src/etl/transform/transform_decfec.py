import logging
import pandas as pd
from src.etl.contract import build_transform_result, TRANSFORM_CONTRACT_VERSION

logger = logging.getLogger(__name__)

def transform_decfec(df: pd.DataFrame):
    df_work = df.copy(deep=True)
    total_input = len(df_work)

    valid_docs = []
    rejected_docs = []

    for _, row in df_work.iterrows():
        try:
            row_dict = row.to_dict()

            # Mapeamento e limpeza dos campos
            sig_agente     = str(row.get("SigAgente")).strip() if row.get("SigAgente") else None
            code           = str(row.get("IdeConjUndConsumidoras")).strip() if row.get("IdeConjUndConsumidoras") else None
            sig_indicador  = str(row.get("SigIndicador")).strip() if row.get("SigIndicador") else None
            ano            = pd.to_numeric(row.get("AnoIndice"), errors="coerce")
            periodo        = pd.to_numeric(row.get("NumPeriodoIndice"), errors="coerce")
            
            valor_str = str(row.get("VlrIndiceEnviado") or "").strip().replace(",", ".")
            valor     = pd.to_numeric(valor_str, errors="coerce")

            if not sig_agente or not code or not sig_indicador or pd.isna(ano) or pd.isna(periodo):
                rejected_docs.append({
                    "row": row_dict,
                    "reason": "Missing required fields (mapped)"
                })
                continue

            doc = {
                "SigAgente": sig_agente,
                "IdeConjUndConsumidoras": code,
                "SigIndicador": sig_indicador,
                "AnoIndice": int(ano),
                "NumPeriodoIndice": int(periodo),
                "VlrIndiceEnviado": valor
            }

            valid_docs.append(doc)
            
        except Exception as e:
            logger.error(f"Error processing row: {str(e)}")
            rejected_docs.append({"row": row.to_dict(),"reason": f"Exception: {str(e)}"})
            
        result = build_transform_result(valid_docs, rejected_docs, total_input)
        result["contract_version"] = TRANSFORM_CONTRACT_VERSION
    return result