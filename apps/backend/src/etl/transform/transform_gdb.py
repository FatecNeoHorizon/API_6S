import logging
from bson import ObjectId
from src.etl.utils.contract import build_transform_result
from src.etl.utils.transform_functions import (
    _to_str,
    _to_float,
    _strip_columns
)

logger = logging.getLogger(__name__)

def transform_gdb(chunk, layer_name: str, geodatabase_id: str) -> dict:
    layer_name = layer_name.upper().strip()
    total_input = len(chunk)
    chunk = _strip_columns(chunk)
    
    valid_docs = []
    rejected_docs = []

    if layer_name not in ["CONJ", "SUB", "UN_TRA_D"]:
        return build_transform_result([], [], total_input)

    for row in chunk.to_dict(orient="records"):
        try:
            if layer_name == "CONJ":
                # Mapeamento para Conjuntos
                conj_name = _to_str(row.get("NOM")) # Use nomes específicos para evitar confusão
                code = _to_str(row.get("COD_ID"))

                if not conj_name or not code:
                    rejected_docs.append({
                        "row": row,
                        "reason": "Missing NOM or COD_ID in CONJ"})
                    continue

                valid_docs.append({
                    "name": conj_name,
                    "code": code,
                    "geometry": row.get("geometry_geojson"),
                    "geodatabase_id": ObjectId(geodatabase_id),  # ← adiciona aqui também
                    "layer_source": layer_name
                })

            elif layer_name == "SUB":
                sub_code = _to_str(row.get("COD_ID")) 
                sub_dist = _to_str(row.get("DIST"))
                sub_descr = _to_str(row.get("DESCR"))

                if not sub_code:
                    rejected_docs.append({"row": row, "reason": "Missing COD_ID in SUB"})
                    continue

                valid_docs.append({
                    "code": sub_code,
                    "distributor_code": sub_dist,
                    "description": sub_descr,
                    "geometry": row.get("geometry_geojson"),
                    "geodatabase_id": ObjectId(geodatabase_id),
                    "layer_source": layer_name
                })

            elif layer_name == "UN_TRA_D":
                code             = _to_str(row.get("COD_ID"))
                distributor_code = _to_str(row.get("DIST"))
                description      = _to_str(row.get("DESCR"))
                status           = _to_str(row.get("SIT_ATIV"))
                location_area    = _to_str(row.get("ARE_LOC"))
                nominal_power_kva = _to_float(row.get("POT_NOM"))
                iron_losses_kw   = _to_float(row.get("PER_FER"))
                copper_losses_kw = _to_float(row.get("PER_COB"))

                if not code:
                    rejected_docs.append({"row": row, "reason": "Missing COD_ID in UN_TRA_D"})
                    continue

                valid_docs.append({
                    "code":              code,
                    "distributor_code":  distributor_code,
                    "description":       description,
                    "status":            status,
                    "location_area":     location_area,
                    "nominal_power_kva": nominal_power_kva,
                    "iron_losses_kw":    iron_losses_kw,
                    "copper_losses_kw":  copper_losses_kw,
                    "layer_source":      layer_name,
                })

        except Exception as e:
            logger.error(f"Erro no processamento da linha: {str(e)}")
            rejected_docs.append({"row": row, "reason": f"Exception: {str(e)}"})

    logger.info(f"Transformer completo para {layer_name}: {len(valid_docs)} válidos, {len(rejected_docs)} rejeitados, do {total_input} total")
    return build_transform_result(valid_docs, rejected_docs, total_input)