"""
Time Series Forecasting Procedures for distribution indicators.

Handles training RandomForest models and generating forecasts for DEC/FEC indicators
using MongoDB data via query_mongo_timeseries module.
"""

from datetime import datetime, timezone
from typing import Optional
import pandas as pd
import numpy as np
import joblib
import os
import gc
from pathlib import Path

import pymongo
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from src.config.settings import Settings
from src.database.connection import get_client
from src.etl.query_mongo_timeseries import prepare_timeseries


_settings = Settings()


class TimeSeriesForecastProcedures:
    """
    Procedures for training time series forecasting models for distribution indicators.
    
    Workflow:
    1. Query MongoDB for indicator data (DEC/FEC)
    2. Prepare time series with lag features
    3. Train RandomForest model (80% train, 20% test)
    4. Generate 12-month forecasts
    5. Return models, metrics, and predictions
    """
    
    connection: Optional[pymongo.MongoClient]
    db: Optional[pymongo.database.Database]
    models_dir: Path
    
    def __init__(
        self,
        connection: Optional[pymongo.MongoClient] = None,
        models_dir: Optional[str] = None,
    ):
        """
        Initialize procedures with optional MongoDB connection.
        
        Args:
            connection: MongoDB client instance. If not provided, creates new.
            models_dir: Directory to save trained models. Defaults to /tmp/models.
        """
        if connection is not None:
            self.connection = connection
        else:
            self.connection = get_client()
        
        self.db = self.connection[_settings.mongo_db_name]
        
        self.models_dir = Path(models_dir or "/tmp/models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def train_forecast_model(
        self,
        consumer_unit_set_id: str,
        indicator_type_code: str,
        year_start: int,
        year_end: int,
        n_lags: int = 12,
        min_records: int = 20,
        test_split: float = 0.2,
        random_state: int = 42,
    ) -> dict:
        """
        Train a RandomForest model for a specific indicator.
        
        Args:
            consumer_unit_set_id: Unit ID (e.g., "16648")
            indicator_type_code: "DEC" or "FEC"
            year_start: Start year (inclusive)
            year_end: End year (inclusive)
            n_lags: Number of lag features (default: 12)
            min_records: Minimum records required (default: 20)
            test_split: Test set fraction (default: 0.2 → 80/20)
            random_state: Random seed for reproducibility
            
        Returns:
            Dictionary with keys:
                - success (bool)
                - model (sklearn model or None)
                - mae (float)
                - n_train (int)
                - n_test (int)
                - n_records (int)
                - message (str)
        """
        try:
            # Step 1: Prepare time series data
            result = prepare_timeseries(
                consumer_unit_set_id=consumer_unit_set_id,
                indicator_type_code=indicator_type_code,
                year_start=year_start,
                year_end=year_end,
                n_lags=n_lags,
                min_records=min_records,
                connection=self.connection,
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "model": None,
                    "mae": None,
                    "n_train": None,
                    "n_test": None,
                    "n_records": result["record_count"],
                    "message": f"Data preparation failed: {result['message']}",
                }
            
            df = result["df"]
            
            # Step 2: Extract features and target
            lag_cols = [f"lag_{i}" for i in range(1, n_lags + 1)]
            df_clean = df.dropna(subset=lag_cols + ["VlrIndiceEnviado"]).reset_index(drop=True)
            
            if df_clean.empty:
                return {
                    "success": False,
                    "model": None,
                    "mae": None,
                    "n_train": None,
                    "n_test": None,
                    "n_records": len(df),
                    "message": "No valid records after removing NaNs",
                }
            
            X = df_clean[lag_cols]
            y = df_clean["VlrIndiceEnviado"]
            
            # Step 3: Split data
            split_idx = int(len(df_clean) * (1 - test_split))
            X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
            y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
            
            # Step 4: Train model
            model = RandomForestRegressor(
                n_estimators=100,
                n_jobs=-1,
                random_state=random_state,
            )
            model.fit(X_train, y_train)
            
            # Step 5: Evaluate
            mae = mean_absolute_error(y_test, model.predict(X_test))
            
            gc.collect()
            
            return {
                "success": True,
                "model": model,
                "mae": mae,
                "n_train": len(X_train),
                "n_test": len(X_test),
                "n_records": len(df),
                "message": f"Model trained successfully (MAE: {mae:.4f})",
            }
        
        except Exception as exc:
            return {
                "success": False,
                "model": None,
                "mae": None,
                "n_train": None,
                "n_test": None,
                "n_records": None,
                "message": f"Training failed: {str(exc)}",
            }
    
    def generate_forecasts(
        self,
        model,
        consumer_unit_set_id: str,
        indicator_type_code: str,
        year_start: int,
        year_end: int,
        n_lags: int = 12,
        forecast_months: int = 12,
    ) -> dict:
        """
        Generate N-month forecasts using a trained model.
        
        Args:
            model: Trained sklearn model
            consumer_unit_set_id: Unit ID
            indicator_type_code: "DEC" or "FEC"
            year_start: Data start year
            year_end: Data end year
            n_lags: Number of lag features used in model
            forecast_months: Number of months to forecast (default: 12)
            
        Returns:
            Dictionary with keys:
                - success (bool)
                - forecasts (list[dict]): List of {data, previsao}
                - message (str)
        """
        try:
            if model is None:
                return {
                    "success": False,
                    "forecasts": [],
                    "message": "Model is None",
                }
            
            # Get historical data
            result = prepare_timeseries(
                consumer_unit_set_id=consumer_unit_set_id,
                indicator_type_code=indicator_type_code,
                year_start=year_start,
                year_end=year_end,
                n_lags=n_lags,
                connection=self.connection,
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "forecasts": [],
                    "message": f"Failed to load data: {result['message']}",
                }
            
            df = result["df"]
            lag_cols = [f"lag_{i}" for i in range(1, n_lags + 1)]
            
            # Get last valid values for lags
            df_valid = df.dropna(subset=["VlrIndiceEnviado"])
            if df_valid.empty:
                return {
                    "success": False,
                    "forecasts": [],
                    "message": "No valid historical data",
                }
            
            historico = list(df_valid["VlrIndiceEnviado"].values)
            last_date = df_valid["data"].iloc[-1]
            
            # Generate forecasts
            forecasts = []
            for m in range(1, forecast_months + 1):
                nova_data = pd.Timestamp(last_date) + pd.DateOffset(months=m)
                lags = historico[-n_lags:][::-1]
                pred = model.predict(
                    pd.DataFrame([lags], columns=lag_cols)
                )[0]
                
                forecasts.append({
                    "data": nova_data.strftime("%Y-%m-%d"),
                    "previsao": float(pred),
                })
                
                historico.append(pred)
            
            return {
                "success": True,
                "forecasts": forecasts,
                "message": f"Generated {forecast_months} forecasts",
            }
        
        except Exception as exc:
            return {
                "success": False,
                "forecasts": [],
                "message": f"Forecast generation failed: {str(exc)}",
            }
    
    def generate_forecasts_for_persistence(
        self,
        model,
        consumer_unit_set_id: str,
        indicator_type_code: str,
        year_start: int,
        year_end: int,
        n_lags: int = 12,
    ) -> dict:
        """
        Generate forecasts formatted for MongoDB persistence.
        
        Returns list of documents with structure:
        {
            "consumer_unit_set_id": str,
            "indicator": str,
            "forecast_date": str (YYYY-MM-DD),
            "forecast_value": float,
            "model": str,
            "generated_on": datetime
        }
        """
        forecast_months = _settings.model_forecast_months
        
        # Get forecast result using existing method
        forecast_result = self.generate_forecasts(
            model=model,
            consumer_unit_set_id=consumer_unit_set_id,
            indicator_type_code=indicator_type_code,
            year_start=year_start,
            year_end=year_end,
            n_lags=n_lags,
            forecast_months=forecast_months,
        )
        
        if not forecast_result["success"]:
            return {
                "success": False,
                "predictions": [],
                "message": forecast_result["message"],
            }
        
        forecasts = forecast_result["forecasts"]
        now = datetime.now(timezone.utc)
        
        # Transform to persistence format
        predictions = []
        for forecast in forecasts:
            prediction = {
                "consumer_unit_set_id": consumer_unit_set_id,
                "indicator": indicator_type_code,
                "forecast_date": forecast["data"],  # Already in YYYY-MM-DD format
                "forecast_value": forecast["previsao"],
                "model": "RandomForestRegressor",
                "generated_on": now,
            }
            predictions.append(prediction)
        
        return {
            "success": True,
            "predictions": predictions,
            "message": f"Generated {len(predictions)} predictions for persistence",
        }
    
    def forecast_for_unit(
        self,
        consumer_unit_set_id: str,
        year_start: int = 2015,
        year_end: int = 2024,
        indicator_types: Optional[list] = None,
        save_models: bool = True,
    ) -> dict:
        """
        Complete pipeline: train DEC and FEC models, generate forecasts.
        
        Args:
            consumer_unit_set_id: Unit ID (e.g., "16648")
            year_start: Start year
            year_end: End year
            indicator_types: List of indicators to forecast (default: ["DEC", "FEC"])
            save_models: Whether to save trained models to disk
            
        Returns:
            Dictionary with keys:
                - success (bool)
                - consumer_unit_id (str)
                - metrics (dict): {indicator: {mae, n_train, n_test}}
                - forecasts (list[dict]): Consolidated forecasts
                - models (dict): {indicator: model} (if save_models=False)
                - message (str)
        """
        if indicator_types is None:
            indicator_types = ["DEC", "FEC"]
        
        metrics = {}
        all_forecasts = []
        models = {}
        
        for indicator in indicator_types:
            print(f"\n[{indicator}] Training model...")
            
            # Train model
            train_result = self.train_forecast_model(
                consumer_unit_set_id=consumer_unit_set_id,
                indicator_type_code=indicator,
                year_start=year_start,
                year_end=year_end,
            )
            
            if not train_result["success"]:
                print(f"  ✗ {train_result['message']}")
                metrics[indicator] = {
                    "success": False,
                    "message": train_result["message"],
                }
                continue
            
            model = train_result["model"]
            mae = train_result["mae"]
            
            print(f"  ✓ Model trained (MAE: {mae:.4f})")
            
            metrics[indicator] = {
                "success": True,
                "mae": mae,
                "n_train": train_result["n_train"],
                "n_test": train_result["n_test"],
                "n_records": train_result["n_records"],
            }
            
            # Save model if requested
            if save_models:
                model_path = self.models_dir / f"modelo_{indicator}_{consumer_unit_set_id}.pkl"
                joblib.dump(model, str(model_path))
                print(f"  ✓ Model saved: {model_path}")
            else:
                models[indicator] = model
            
            # Generate forecasts
            print(f"[{indicator}] Generating forecasts...")
            forecast_result = self.generate_forecasts(
                model=model,
                consumer_unit_set_id=consumer_unit_set_id,
                indicator_type_code=indicator,
                year_start=year_start,
                year_end=year_end,
                forecast_months=_settings.model_forecast_months,
            )
            
            if not forecast_result["success"]:
                print(f"  ✗ {forecast_result['message']}")
                continue
            
            forecasts = forecast_result["forecasts"]
            print(f"  ✓ Generated {len(forecasts)} forecasts")
            
            # Add indicator info to each forecast
            for f in forecasts:
                f["consumer_unit_id"] = consumer_unit_set_id
                f["indicator"] = indicator
                all_forecasts.append(f)
        
        return {
            "success": len(metrics) > 0,
            "consumer_unit_id": consumer_unit_set_id,
            "year_range": f"{year_start}-{year_end}",
            "metrics": metrics,
            "forecasts": all_forecasts,
            "models": models if not save_models else None,
            "models_directory": str(self.models_dir) if save_models else None,
            "message": f"Processed {len(indicator_types)} indicators",
        }


if __name__ == "__main__":
    # Quick test
    print("=" * 70)
    print("Testing TimeSeriesForecastProcedures")
    print("=" * 70)
    
    procedures = TimeSeriesForecastProcedures()
    
    result = procedures.forecast_for_unit(
        consumer_unit_set_id="16648",
        year_start=2015,
        year_end=2024,
        indicator_types=["DEC", "FEC"],
        save_models=True,
    )
    
    if result["success"]:
        print(f"\n✓ {result['message']}")
        print(f"\nMetrics:")
        for indicator, metrics_data in result["metrics"].items():
            if metrics_data.get("success"):
                print(f"  {indicator}: MAE = {metrics_data['mae']:.4f}")
        
        print(f"\nForecasts: {len(result['forecasts'])} total")
        if result["forecasts"]:
            print(f"  Sample: {result['forecasts'][0]}")
        
        print(f"\nModels saved to: {result['models_directory']}")
    else:
        print(f"\n✗ {result['message']}")
        print(result)
