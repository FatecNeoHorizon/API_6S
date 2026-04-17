from typing import Generator
import pandas as pd
from src.etl.get_decfec_file import get_filepath
from src.etl.transform.transform_decfec import transform_decfec

FILTRO_INDICADORES = [
    'DEC', 'DEC1i', 'DEC1x', 'DECINC', 'DECIND', 'DECINE', 'DECINO',
    'DECIP', 'DECIPC', 'DECXN', 'DECXNC', 'DECXP', 'DECXPC', 'DECi',
    'DECx', 'Dec1', 'Dec1r', 'Decr', 'FEC', 'FEC1i', 'FEC1x', 'FECINC',
    'FECIND', 'FECINE', 'FECINO', 'FECIP', 'FECIPC', 'FECXN', 'FECXNC',
    'FECXP', 'FECXPC', 'FECi', 'FECx', 'Fec1', 'Fec1r', 'Fecr',
]

CHUNK_SIZE = 100_000

def extract_decfec() -> Generator[tuple[pd.DataFrame, str], None, None]:
    source_file = get_filepath()

    for chunk_df in pd.read_csv(
        source_file,
        sep=";",
        encoding="latin-1",
        low_memory=True,
        chunksize=CHUNK_SIZE,
    ):
        chunk_df = chunk_df[chunk_df["SigIndicador"].isin(FILTRO_INDICADORES)]
        chunk_df = transform_decfec(chunk_df)
        chunk_df = chunk_df.drop_duplicates().reset_index(drop=True)
        yield chunk_df, source_file