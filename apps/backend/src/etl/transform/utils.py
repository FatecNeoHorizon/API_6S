import math
from datetime import datetime, date
import pandas as pd


def _to_str(value) -> str | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return str(value).strip() or None


def _to_float(value) -> float | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    try:
        return float(str(value).replace(',', '.'))
    except (ValueError, TypeError):
        return None


def _to_int(value) -> int | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def _to_date(value) -> str | None:
    if value is None:
        return None

    if isinstance(value, (datetime, date)):
        return value.strftime('%Y-%m-%d')

    try:
        return datetime.strptime(str(value).strip(), '%d%b%Y').strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return None


def _strip_columns(df: pd.DataFrame) -> pd.DataFrame:
    str_cols = df.select_dtypes(include='object').columns
    df[str_cols] = df[str_cols].apply(
        lambda col: col.map(lambda value: value.strip() if isinstance(value, str) else value)
    )
    return df