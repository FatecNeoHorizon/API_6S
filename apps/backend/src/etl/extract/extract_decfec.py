from typing import Generator
import pandas as pd
from pathlib import Path

INDICATORS_FILTER_NEW = ['DEC', "FEC"]

CHUNK_SIZE = 100_000

def extract_decfec(path: Path) -> Generator[tuple[pd.DataFrame, str], None, None]:
    """
    Yields chunks of DECFEC data as tuples (chunk_df, source_file).
    
    Args:
        path: Path to the CSV file
        
    Yields:
        Tuples of (chunk_df, source_file) where chunk_df is a pandas DataFrame
        and source_file is the string path to the source file
    """
    df = pd.read_csv(path, sep=";", encoding="latin-1")
    df = df[df['SigIndicador'].isin(INDICATORS_FILTER_NEW)]
    df = df.drop(columns=['DatGeracaoConjuntoDados'])
    
    source_file_str = str(path)
    
    # Yield chunks of CHUNK_SIZE rows
    for i in range(0, len(df), CHUNK_SIZE):
        chunk_df = df.iloc[i:i+CHUNK_SIZE]
        yield chunk_df, source_file_str