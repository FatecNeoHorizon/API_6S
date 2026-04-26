from etl.transform.utils import (
    _to_str,
    _to_int,
    _to_float,
    _strip_columns
)

REQUIRED = [
    "agent_acronym",
    "consumer_unit_set_id",
    "indicator_type_code",
    "year",
    "period"
]

def transform_distribution_indices(df):
    df = _strip_columns(df)

    documents = []
    rejected = []

    for _, row in df.iterrows():
        doc = {
            "agent_acronym": _to_str(row.get("SigAgente")),
            "cnpj_number": _to_str(row.get("NumCNPJ")),
            "consumer_unit_set_id": _to_str(row.get("IdeConjUndConsumidoras")),
            "consumer_unit_set_description": _to_str(row.get("DscConjUndConsumidoras")),
            "indicator_type_code": _to_str(row.get("SigIndicador")),
            "year": _to_int(row.get("Ano")),
            "period": _to_int(row.get("IndexPeriodNumber")),
            "value": _to_float(row.get("VlrIndiceEnviado")),
        }

        if any(doc[field] is None for field in REQUIRED):
            rejected.append({
                "row": row.to_dict(),
                "reason": "Missing required fields"
            })
            continue

        documents.append(doc)

    return {
        "valid": documents,
        "rejected": rejected
    }