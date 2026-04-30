import json
import pandas as pd
from pathlib import Path

def extract_losses(path: Path) -> list[dict]:
    df = pd.read_excel(path)
    return json.loads(df.to_json(orient="records", force_ascii=False))