from typing import Generator
import pandas as pd
from pathlib import Path

INDICATORS_FILTER_NEW = ['DEC', "FEC"]

CHUNK_SIZE = 100_000

def extract_decfec(path: Path) -> list[dict]:
    df = pd.read_csv(path, sep=";", encoding="latin-1")
    df = df[df['SigIndicador'].isin(INDICATORS_FILTER_NEW)]
    df = df.drop(columns=['DatGeracaoConjuntoDados'])
    return df.to_dict(orient='records')