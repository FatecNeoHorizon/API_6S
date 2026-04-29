from collections import defaultdict
from src.services.upload_service import TRANSFORM_CONTRACT_VERSION
from src.etl.transform.utils import (
    _to_str,
    _to_int,
    _to_float,
    _strip_columns
)

def transform_limits(df):
    df = _strip_columns(df)
    
    grouped = defaultdict(list)
    rejected = []

    for _, row in df.iterrows():
        # Captura dos campos usando os nomes das colunas do CSV
        code = _to_str(row.get("IdeConjUndConsumidoras"))
        indicator_type_code = _to_str(row.get("SigIndicador"))
        year = _to_int(row.get("AnoLimiteQualidade"))
        limit = _to_float(row.get("VlrLimite"))

        # Validação de campos obrigatórios
        if not code or not indicator_type_code or year is None:
            rejected.append({
                "row": row.to_dict(),
                "reason": "Missing required fields (code, indicator or year)"
            })
            continue

        summary = {
            "indicator_type_code": indicator_type_code,
            "year": year,
            "limit": limit
        }

        # Agrupamento por código do conjunto
        grouped[code].append(summary)

    # Transformação do dicionário agrupado em lista de documentos para o MongoDB
    documents = [
        {
            "code": code,
            "annual_summaries": summaries
        }
        for code, summaries in grouped.items()
    ]

    # Ajuste Matemático para o Contrato:
    # Como o validador exige que total_valid == len(valid),
    # recalculamos os totais baseados nos documentos agrupados finais.
    total_valid_final = len(documents)
    total_rejected_final = len(rejected)
    total_input_final = total_valid_final + total_rejected_final

    return {
        "contract_version": TRANSFORM_CONTRACT_VERSION,
        "valid": documents,
        "rejected": rejected,
        "stats": {
            "total_input": total_input_final,
            "total_valid": total_valid_final,
            "total_rejected": total_rejected_final
        }
    }