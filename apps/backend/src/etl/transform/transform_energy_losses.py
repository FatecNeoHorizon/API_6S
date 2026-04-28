import unicodedata

from src.etl.transform.contract import build_transform_result
from src.etl.transform.utils import (
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
    total_input = len(df)

    documents = []
    rejected = []

    for _, row in df.iterrows():

        distributor = _to_str(row.get("Distribuidora"))
        process_date = _to_date(row.get("Data do Processo"))

        doc = {
            "distributor": distributor,
            "distributor_slug": _to_slug(distributor),
            "state": _to_str(row.get("Estado")),
            "uf": _to_str(row.get("UF")),
            "process_date": process_date,

            "tme_brl_mwh": _to_float(row.get("TME (R$/MWh)")),
            "basic_network_loss_mwh": _to_float(row.get("Perdas na Rede Básica (MWh)")),
            "technical_loss_mwh": _to_float(row.get("Perdas Técnicas (MWh)")),
            "non_technical_loss_mwh": _to_float(row.get("Perdas Não Técnicas (MWh)")),

            "basic_network_loss_cost_brl": _to_float(row.get("Custo Perdas na Rede Básica (R$)")),
            "technical_loss_cost_brl": _to_float(row.get("Custo Perdas Técnicas (R$)")),
            "non_technical_loss_cost_brl": _to_float(row.get("Custo Perdas Não Técnicas (R$)")),

            "parcel_b_brl": _to_float(row.get("Parcela B (R$)")),
            "required_revenue_brl": _to_float(row.get("Receita Requerida (R$)")),
        }

        if not distributor or not process_date:
            rejected.append({
                "row": row.to_dict(),
                "reason": "Missing distributor or process_date"
            })
            continue

        documents.append(doc)

    return build_transform_result(valid=documents, rejected=rejected, total_input=total_input)