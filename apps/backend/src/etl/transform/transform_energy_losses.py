import logging
from src.etl.utils.contract import build_transform_result, TRANSFORM_CONTRACT_VERSION
from src.etl.utils.transform_functions import (
    _to_str,
    _to_float,
    _to_date,
    _strip_columns,
    _to_slug

)

def transform_energy_losses(df):
    df = _strip_columns(df)
    total_input = len(df)

    valid_docs = []
    rejected_docs = []

    for _, row in df.iterrows():
        try:
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
                rejected_docs.append({
                    "row": row.to_dict(),
                    "reason": "Missing distributor or process_date"
                })
                continue

            valid_docs.append(doc)

        except Exception as e:
            logging.error(f"Error processing row: {str(e)}")
            rejected_docs.append({
                "row": row.to_dict(),
                "reason": f"Exception: {str(e)}"
            })

    result = build_transform_result(valid_docs, rejected_docs, total_input)
    result["contract_version"] = TRANSFORM_CONTRACT_VERSION
    logging.info(f"Transformer completo: {len(valid_docs)} validos, {len(rejected_docs)} rejeitados, do {total_input} total")
    return result