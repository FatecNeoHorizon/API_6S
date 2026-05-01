from apps.backend.src.etl.transform.transform_gdb import transform_gdb
from pathlib import Path
import geopandas as gpd

path = Path('/app/tmp/uploads/1ae0dd2aa98c49f0a4d4ac4f76b84867/gdb_extracted/EDP_SP_391_2016-12-31_M6_20170707-0903.gdb')

layer_name = "CONJ"
geodatabase_id = "teste_gdb"

gdf = gpd.read_file(path, layer=layer_name)

gdf["geometry_geojson"] = gdf["geometry"].apply(
    lambda geom: geom.__geo_interface__ if geom else None
)

result = transform_gdb(gdf, layer_name, geodatabase_id)

docs = result.get("docs", [])
rejected = result.get("rejected", [])

print("Docs:", len(docs))
print("Rejected:", len(rejected))

if docs:
    print("Primeiro doc:", docs[0])
else:
    print("Nenhum documento válido gerado")