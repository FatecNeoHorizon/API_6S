import pandas as pd
from datetime import datetime
from typing import Optional
from src.control.distribution_indices_procedures import Distribution_indices_procedures
from src.config.settings import Settings
import pymongo

def convert_year_period_to_date(year: int, period: int) -> datetime:
    """
    Convert (year, period) where period is 1-12 to a datetime object.
    
    Args:
        year: Full year (e.g., 2024)
        period: Month (1-12)
        
    Returns:
        datetime object representing the first day of the month
    """
    return pd.to_datetime(f"{year:04d}-{period:02d}-01")


def query_indicators_for_unit(
    consumer_unit_set_id: str,
    indicator_type_code: str,
    year_start: int,
    year_end: int,
    connection: Optional[pymongo.MongoClient] = None,
) -> list[dict]:
    """
    Query MongoDB for indicators matching the unit and type.
    
    Args:
        consumer_unit_set_id: Unit ID (e.g., "16648")
        indicator_type_code: Indicator type ("DEC" or "FEC")
        year_start: Minimum year (inclusive)
        year_end: Maximum year (inclusive)
        connection: MongoDB connection (optional; creates new if not provided)
        
    Returns:
        List of documents from distribution_indices collection
    """
    filter_dict = {
        "consumer_unit_set_id": consumer_unit_set_id,
        "indicator_type_code": indicator_type_code,
        "year": {"$gte": year_start, "$lte": year_end},
    }
    
    procedures = Distribution_indices_procedures(connection=connection)
    # Note: getAll() returns validated Pydantic models; we convert to dicts
    results = procedures.getAll(filter_dict)
    return [r.model_dump() for r in results]


def prepare_timeseries_dataframe(
    consumer_unit_set_id: str,
    indicator_type_code: str,
    year_start: int,
    year_end: int,
    connection: Optional[pymongo.MongoClient] = None,
) -> pd.DataFrame:
    """
    Query MongoDB and convert to a sorted DataFrame with date index.
    
    Args:
        consumer_unit_set_id: Unit ID (e.g., "16648")
        indicator_type_code: Indicator type ("DEC" or "FEC")
        year_start: Minimum year (inclusive)
        year_end: Maximum year (inclusive)
        connection: MongoDB connection (optional)
        
    Returns:
        DataFrame with columns [data, VlrIndiceEnviado] sorted by date
        Returns empty DataFrame if no data found
    """
    records = query_indicators_for_unit(
        consumer_unit_set_id=consumer_unit_set_id,
        indicator_type_code=indicator_type_code,
        year_start=year_start,
        year_end=year_end,
        connection=connection,
    )
    
    if not records:
        return pd.DataFrame(columns=["data", "VlrIndiceEnviado"])
    
    # Convert to DataFrame
    df = pd.DataFrame(records)
    
    # Create date column from year + period
    df["data"] = df.apply(
        lambda row: convert_year_period_to_date(row["year"], row["period"]),
        axis=1
    )
    
    # Keep only necessary columns
    df = df[["data", "value"]].copy()
    df.columns = ["data", "VlrIndiceEnviado"]
    
    # Sort by date
    df = df.sort_values("data").reset_index(drop=True)
    
    # Convert value to float
    df["VlrIndiceEnviado"] = pd.to_numeric(df["VlrIndiceEnviado"], errors="coerce")
    
    return df


def create_lag_features(
    df: pd.DataFrame,
    n_lags: int = 12,
    value_column: str = "VlrIndiceEnviado",
) -> pd.DataFrame:
    """
    Create lag features for time series modeling.
    
    Args:
        df: DataFrame with time series data
        n_lags: Number of lags to create (default: 12 for monthly data)
        value_column: Name of the value column to lag
        
    Returns:
        DataFrame with original columns + lag_1 to lag_n columns
    """
    df_work = df.copy()
    
    for i in range(1, n_lags + 1):
        df_work[f"lag_{i}"] = df_work[value_column].shift(i)
    
    return df_work


def validate_timeseries_data(
    df: pd.DataFrame,
    min_records: int = 20,
) -> tuple[bool, str]:
    """
    Validate time series data before model training.
    
    Args:
        df: DataFrame to validate
        min_records: Minimum required records
        
    Returns:
        Tuple of (is_valid, message)
    """
    if df.empty:
        return False, "DataFrame vazio"
    
    if len(df) < min_records:
        return False, f"Apenas {len(df)} registros (mínimo: {min_records})"
    
    if df["VlrIndiceEnviado"].isna().all():
        return False, "Todos os valores são NaN"
    
    return True, "OK"


def prepare_timeseries(
    consumer_unit_set_id: str,
    indicator_type_code: str,
    year_start: int,
    year_end: int,
    n_lags: int = 12,
    min_records: int = 20,
    connection: Optional[pymongo.MongoClient] = None,
) -> dict:
    """
    Complete pipeline: query MongoDB → prepare DataFrame → create lags → validate.
    
    Args:
        consumer_unit_set_id: Unit ID (e.g., "16648")
        indicator_type_code: Indicator type ("DEC" or "FEC")
        year_start: Minimum year (inclusive)
        year_end: Maximum year (inclusive)
        n_lags: Number of lag features (default: 12)
        min_records: Minimum records required (default: 20)
        connection: MongoDB connection (optional)
        
    Returns:
        Dictionary with keys:
            - success (bool): Whether preparation succeeded
            - df (pd.DataFrame): Prepared DataFrame or empty if failed
            - message (str): Status message
            - record_count (int): Number of records loaded
    """
    # Step 1: Query and prepare DataFrame
    df = prepare_timeseries_dataframe(
        consumer_unit_set_id=consumer_unit_set_id,
        indicator_type_code=indicator_type_code,
        year_start=year_start,
        year_end=year_end,
        connection=connection,
    )
    
    record_count = len(df)
    
    # Step 2: Validate before lag creation
    is_valid, validation_msg = validate_timeseries_data(df, min_records=min_records)
    
    if not is_valid:
        return {
            "success": False,
            "df": pd.DataFrame(),
            "message": f"Validação falhou: {validation_msg}",
            "record_count": record_count,
        }
    
    # Step 3: Create lag features
    df = create_lag_features(df, n_lags=n_lags)
    
    return {
        "success": True,
        "df": df,
        "message": f"OK - {record_count} registros carregados, lags criados",
        "record_count": record_count,
    }


if __name__ == "__main__":
    # Quick test
    result = prepare_timeseries(
        consumer_unit_set_id="16648",
        indicator_type_code="DEC",
        year_start=2015,
        year_end=2024,
    )
    
    if result["success"]:
        print(f"✓ {result['message']}")
        print(f"DataFrame shape: {result['df'].shape}")
        print(result['df'].head())
    else:
        print(f"✗ {result['message']}")
