import pandas as pd
from src.etl.transform.contract import TRANSFORM_CONTRACT_VERSION


def transform_decfec(df: pd.DataFrame):
    df_work = df.copy(deep=True)
    total_input = len(df_work)

    valid = []
    rejected = []

    for _, row in df_work.iterrows():
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
            rejected.append({
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

        valid.append(doc)

    # Retorno estruturado EXATAMENTE como o _validate_transform_contract exige
    return {
        "contract_version": TRANSFORM_CONTRACT_VERSION,
        "valid": valid,
        "rejected": rejected,
        "stats": {
            "total_input": total_input,
            "total_valid": len(valid),
            "total_rejected": len(rejected)
        }
    }