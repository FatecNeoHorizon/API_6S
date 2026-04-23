from typing import Generator
import pandas as pd
from src.etl.get_decfec_file import get_filepath
from src.etl.transform.transform_decfec import transform_decfec
from src.utils.find_uploaded_file import find_file_full_path
import os
from pathlib import Path

FILTRO_INDICADORES = [
    'DEC', 'DEC1i', 'DEC1x', 'DECINC', 'DECIND', 'DECINE', 'DECINO',
    'DECIP', 'DECIPC', 'DECXN', 'DECXNC', 'DECXP', 'DECXPC', 'DECi',
    'DECx', 'Dec1', 'Dec1r', 'Decr', 'FEC', 'FEC1i', 'FEC1x', 'FECINC',
    'FECIND', 'FECINE', 'FECINO', 'FECIP', 'FECIPC', 'FECXN', 'FECXNC',
    'FECXP', 'FECXPC', 'FECi', 'FECx', 'Fec1', 'Fec1r', 'Fecr',
]

INDICATORS_FILTER_NEW = ['DEC', "FEC"]

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

#The list returned can be retrieved with commands such as "data_dict[1]" or data_dict[1]['UF']
#Only the 'DatGeracaoConjuntoDados' column won't be used
def extract_decfec_new():
    file_name = os.getenv("CSV_FILE_NAME")
    search_folder = os.getenv("TMP_UPLOAD_PATH")

    path_value = find_file_full_path(file_name, search_folder)
    
    if not path_value:
        raise ValueError("CSV_FILE_NAME environment variable is not set.")

    path = Path(path_value)

    df : pd.DataFrame = pd.read_csv(path, sep=";", encoding="latin-1")
    df = df[df['SigIndicador'].isin(INDICATORS_FILTER_NEW)]
    df = df.drop(columns=['DatGeracaoConjuntoDados'])
    data_dict = df.to_dict(orient='records')

    #For demonstration purposes, only the first 50 items are returned to be showed on the test endpoint
    return data_dict[0:50]
