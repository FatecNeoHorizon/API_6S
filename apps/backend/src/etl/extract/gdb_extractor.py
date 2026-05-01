import logging
import pyogrio as pyo
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_gdb_generator(path: Path, chunk_size: int = 100):
    raw_layers = pyo.list_layers(path)

    GROUP_1 = ["CONJ", "SUB"]
    GROUP_2 = ["UNTRMT", "UNTRAT"]

    ORDERED_LAYERS = GROUP_1 + GROUP_2

    layer_names = [
        layer for layer in ORDERED_LAYERS
        if layer in [l[0] for l in raw_layers]
    ]

    for layer_name in layer_names:
        logger.info(f"[START] Lendo layer: {layer_name}")

        try:
            gdf = pyo.read_dataframe(path, layer=layer_name)

            logger.info(f"[LOADED] {layer_name} - {len(gdf)} registros")

            if gdf.crs is None:
                raise ValueError(f"Layer {layer_name} sem CRS")

            if gdf.crs.to_epsg() != 4326:
                logger.info(f"[CRS] Convertendo {layer_name}")
                gdf = gdf.to_crs(epsg=4326)

            if "geometry" in gdf.columns:
                logger.info(f"[GEOM] Serializando {layer_name}")
                gdf["geometry_geojson"] = gdf["geometry"].apply(
                    lambda g: g.__geo_interface__ if g else None
                )

            for i in range(0, len(gdf), chunk_size):
                logger.info(f"[CHUNK] {layer_name} - {i}")

                yield gdf.iloc[i:i+chunk_size], layer_name, str(path)

        except Exception as e:
            logger.error(f"[ERROR] {layer_name}: {str(e)}")

            yield {
                "error": str(e),
                "layer_name": layer_name,
                "source_file": str(path)
            }, layer_name, str(path)