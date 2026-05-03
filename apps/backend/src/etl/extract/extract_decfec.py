from collections.abc import Iterator
import pandas as pd
from pathlib import Path

INDICATORS_FILTER_NEW = ['DEC', "FEC"]

CHUNK_SIZE = 100_000

def extract_decfec(path: Path) -> Iterator[dict]:
    """Stream rows from a potentially large CSV as dictionaries.

    Reads the CSV in chunks, filters and drops the unwanted column, and
    yields one record (dict) at a time to avoid high memory usage.
    """
    for chunk in pd.read_csv(path, sep=";", encoding="latin-1", chunksize=CHUNK_SIZE):
        chunk = chunk[chunk['SigIndicador'].isin(INDICATORS_FILTER_NEW)]
        chunk = chunk.drop(columns=['DatGeracaoConjuntoDados'], errors='ignore')
        for record in chunk.to_dict(orient='records'):
            yield record


def extract_decfec_preview(path: Path, limit: int = 50) -> list[dict]:
    """Return a small list of records for preview purposes.

    Consumes the streaming `extract_decfec` generator and returns up to
    `limit` records as a list (safe for API preview endpoints).
    """
    results: list[dict] = []
    for i, rec in enumerate(extract_decfec(path)):
        results.append(rec)
        if i + 1 >= limit:
            break
    return results
