from src.etl.transform.utils import (
    _to_str,
    _to_float,
    _strip_columns
)

def transform_gdb_chunk(chunk, layer_name, geodatabase_id):
    chunk = _strip_columns(chunk)

    docs = []
    rejected = []

    if "geometry" in chunk.columns:
        chunk = chunk.drop(columns=["geometry"])

    for _, row in chunk.iterrows():
        if layer_name == "CONJ":
            name = _to_str(row.get("NOM"))
            code = _to_str(row.get("COD_ID"))

            doc = {
                "name": name,
                "code": code,
                "status": _to_str(row.get("status")),
                "shape_length": _to_float(row.get("Shape_Length")),
                "shape_area": _to_float(row.get("Shape_Area")),
                "geometry": row.get("geometry_geojson"),
                "geodatabase_id": geodatabase_id
            }

            if not name or not code:
                rejected.append({
                    "row": row.to_dict(),
                    "reason": "Missing name or code (CONJ)"
                })
                continue

            docs.append(doc)

        elif layer_name == "SUB":
            code = _to_str(row.get("CodSub"))

            doc = {
                "code": code,
                "distributor_code": _to_str(row.get("CodDistribuidora")),
                "description": _to_str(row.get("NomSub")),
            }

            if not code:
                rejected.append({
                    "row": row.to_dict(),
                    "reason": "Missing code (SUB)"
                })
                continue

            docs.append(doc)

        else:
            return {"docs": [], "rejected": []}

    return {
        "docs": docs,
        "rejected": rejected
    }