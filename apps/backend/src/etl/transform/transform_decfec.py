import pandas as pd
from src.etl.transform.contract import build_transform_result


def transform_decfec(df: pd.DataFrame):
    df_work = df.copy(deep=True)

    valid = []
    rejected = []

    for _, row in df_work.iterrows():
        row_dict = row.to_dict()

        # --- MAPEAMENTO REAL ---
        sig_agente = str(row.get(1)).strip() if row.get(1) else None
        code = str(row.get(3)).strip() if row.get(3) else None
        sig_indicador = str(row.get(5)).strip() if row.get(5) else None

        ano = pd.to_numeric(row.get(6), errors="coerce")
        periodo = pd.to_numeric(row.get(7), errors="coerce")

        # --- TRATAR VALOR QUEBRADO (colunas 7 e 8) ---
        parte_inteira = str(row.get(7)).strip() if row.get(7) else "0"
        parte_decimal = str(row.get(8)).strip() if row.get(8) else ""

        valor_str = (parte_inteira + parte_decimal).replace(",", ".")
        valor = pd.to_numeric(valor_str, errors="coerce")

        # --- VALIDAÇÃO ---
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

    return build_transform_result(
        valid=valid,
        rejected=rejected,
        total_input=len(df_work)
    )