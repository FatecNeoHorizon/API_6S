import pandas as pd
import json
from pathlib import Path
from src.utils.find_uploaded_file import find_file_full_path

def extract_limits(path: Path) -> list[dict]:
    df = pd.read_csv(path, sep=";", encoding="latin-1", low_memory=False)
    df = df.drop(columns=['DatGeracaoConjuntoDados'])
    return json.loads(df.to_json(orient="records", force_ascii=False))