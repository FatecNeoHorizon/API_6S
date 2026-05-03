import logging
from src.etl.contract import build_transform_result
from src.etl.transform.utils import (
    _to_str,
    _strip_columns
)

logger = logging.getLogger(__name__)

def transform_gdb(chunk, layer_name: str, geodatabase_id: str) -> dict:
    layer_name = layer_name.upper().strip()
    total_input = len(chunk)
    chunk = _strip_columns(chunk)
    
    valid_docs = []
    rejected_docs = []

    if layer_name not in ["CONJ", "SUB"]:
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
                    "geodatabase_id": geodatabase_id,
                    "layer_source": layer_name
                })

            elif layer_name == "SUB":
                # Mapeamento para Subestações baseado no seu LOG real:
                # Colunas: 'COD_ID', 'DIST', 'DESCR'
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
                    "geodatabase_id": geodatabase_id,
                    "layer_source": layer_name
                })

        except Exception as e:
            logger.error(f"Erro no processamento da linha: {str(e)}")
            rejected_docs.append({"row": row, "reason": f"Exception: {str(e)}"})

    return build_transform_result(valid_docs, rejected_docs, total_input)