from collections.abc import Iterator
import pandas as pd
from pathlib import Path

INDICATORS_FILTER_NEW = ['DEC', "FEC"]

CHUNK_SIZE = 100_000

def extract_decfec(path: Path, chunk_size: int = CHUNK_SIZE) -> Iterator[tuple[pd.DataFrame, str]]:
    for chunk_df in pd.read_csv(
        path,
        sep=";",
        encoding="latin-1",
        low_memory=False,
        chunksize=chunk_size,
    ):
        filtered = chunk_df[chunk_df["SigIndicador"].isin(INDICATORS_FILTER_NEW)]
        if filtered.empty:
            continue
        filtered = filtered.drop(columns=["DatGeracaoConjuntoDados"], errors="ignore")
        yield filtered, str(path)


def extract_decfec_preview(path: Path, limit: int = 50) -> list[dict]:
    preview: list[dict] = []
    for chunk_df, _source_file in extract_decfec(path):
        remaining = limit - len(preview)
        if remaining <= 0:
            break
        preview.extend(chunk_df.head(remaining).to_dict(orient="records"))
    return preview[:limit]