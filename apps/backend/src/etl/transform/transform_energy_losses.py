import unicodedata

from etl.transform.utils import (
    _to_str,
    _to_float,
    _to_date,
    _strip_columns
)


def _to_slug(value: str) -> str | None:
    if not value:
        return None

    normalized = unicodedata.normalize('NFD', value)
    ascii_str = normalized.encode('ascii', 'ignore').decode('ascii')

    return ascii_str.lower().strip().replace(' ', '-')


def transform_energy_losses(df):
    df = _strip_columns(df)

    documents = []
    rejected = []

    for _, row in df.iterrows():

        distributor = _to_str(row.get("Distribuidor"))
        process_date = _to_date(row.get("Data"))

        doc = {
            "distributor": distributor,
            "distributor_slug": _to_slug(distributor),
            "state": _to_str(row.get("Estado")),
            "uf": _to_str(row.get("UF")),
            "process_date": process_date,

            "tme_brl_mwh": _to_float(row.get("TME")),
            "basic_network_loss_mwh": _to_float(row.get("Perda Básica")),
            "technical_loss_mwh": _to_float(row.get("Perda Técnica")),
            "non_technical_loss_mwh": _to_float(row.get("Perda Não Técnica")),

            "basic_network_loss_cost_brl": _to_float(row.get("Custo Básico")),
            "technical_loss_cost_brl": _to_float(row.get("Custo Técnico")),
            "non_technical_loss_cost_brl": _to_float(row.get("Custo Não Técnico")),

            "parcel_b_brl": _to_float(row.get("Parcela B")),
            "required_revenue_brl": _to_float(row.get("Receita Requerida")),
        }

        if not distributor or not process_date:
            rejected.append({
                "row": row.to_dict(),
                "reason": "Missing distributor or process_date"
            })
            continue

        documents.append(doc)

    return {
        "valid": documents,
        "rejected": rejected
    }