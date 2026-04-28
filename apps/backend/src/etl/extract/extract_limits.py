import pandas as pd
from collections.abc import Iterator
from pathlib import Path

CHUNK_SIZE = 100_000


def extract_limits(path: Path, chunk_size: int = CHUNK_SIZE) -> Iterator[tuple[pd.DataFrame, str]]:
    for chunk_df in pd.read_csv(
        path,
        sep=";",
        encoding="latin-1",
        low_memory=False,
        chunksize=chunk_size,
    ):
        transformed = chunk_df.drop(columns=["DatGeracaoConjuntoDados"], errors="ignore")
        if transformed.empty:
            continue
        yield transformed, str(path)


def extract_limits_preview(path: Path, limit: int = 50) -> list[dict]:
    preview: list[dict] = []
    for chunk_df, _source_file in extract_limits(path):
        remaining = limit - len(preview)
        if remaining <= 0:
            break
        preview.extend(chunk_df.head(remaining).to_dict(orient="records"))
    return preview[:limit]