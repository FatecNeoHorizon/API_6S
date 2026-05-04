"""
Unit tests for retraining_service.py

Tests cover:
- retrain_for_load grouping and filtering
- Respect of MODEL_RETRAIN_MIN_NEW_RECORDS
- Correct calls to TimeSeriesForecastProcedures
- schedule_retraining threading
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from src.services.retraining_service import retrain_for_load, schedule_retraining


class TestRetrainForLoad:
    """Tests for retrain_for_load function"""

    @patch("src.services.retraining_service.TimeSeriesForecastProcedures")
    @patch("src.services.retraining_service.get_client")
    def test_retrain_for_load_groups_by_unit_and_indicator(self, mock_get_client, mock_procedures_class):
        """Test that retrain_for_load correctly groups records by consumer_unit_set_id and indicator_type_code"""
        
        # Setup mock MongoDB client
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        
        # Mock documents returned by MongoDB
        mock_collection.find.return_value = [
            {"consumer_unit_set_id": "unit1", "indicator_type_code": "DEC", "year": 2020},
            {"consumer_unit_set_id": "unit1", "indicator_type_code": "DEC", "year": 2021},
            {"consumer_unit_set_id": "unit1", "indicator_type_code": "FEC", "year": 2020},
            {"consumer_unit_set_id": "unit2", "indicator_type_code": "DEC", "year": 2020},
        ]
        
        # Mock TimeSeriesForecastProcedures
        mock_procedures_instance = MagicMock()
        mock_procedures_class.return_value = mock_procedures_instance
        mock_procedures_instance.forecast_for_unit.return_value = {
            "success": True,
            "message": "Model trained"
        }
        
        # Call retrain_for_load
        result = retrain_for_load("load_123")
        
        # Assertions
        assert len(result) == 3  # 3 groups
        assert mock_procedures_instance.forecast_for_unit.call_count == 3
        
        # Verify grouping: unit1/DEC should be called once with combined years
        calls = mock_procedures_instance.forecast_for_unit.call_args_list
        consumer_units = [call[1]["consumer_unit_set_id"] for call in calls]
        indicators = [call[1]["indicator_types"][0] for call in calls]  # indicator_types is a list
        
        assert "unit1" in consumer_units
        assert "unit2" in consumer_units
        assert "DEC" in indicators
        assert "FEC" in indicators

    @patch("src.services.retraining_service.TimeSeriesForecastProcedures")
    @patch("src.services.retraining_service.get_client")
    @patch("src.services.retraining_service.settings")
    def test_retrain_respects_min_records_threshold(self, mock_settings, mock_get_client, mock_procedures_class):
        """Test that retrain_for_load skips groups with fewer than MODEL_RETRAIN_MIN_NEW_RECORDS"""
        
        # Setup settings
        mock_settings.mongo_db_name = "test_db"
        mock_settings.model_retrain_min_new_records = 2
        
        # Setup mock MongoDB client
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        
        # Mock documents: unit1/DEC has 2 records (meets threshold), unit2/FEC has 1 (below threshold)
        mock_collection.find.return_value = [
            {"consumer_unit_set_id": "unit1", "indicator_type_code": "DEC", "year": 2020},
            {"consumer_unit_set_id": "unit1", "indicator_type_code": "DEC", "year": 2021},
            {"consumer_unit_set_id": "unit2", "indicator_type_code": "FEC", "year": 2020},
        ]
        
        # Mock TimeSeriesForecastProcedures
        mock_procedures_instance = MagicMock()
        mock_procedures_class.return_value = mock_procedures_instance
        
        # Call retrain_for_load
        result = retrain_for_load("load_123")
        
        # Should only call forecast_for_unit once (unit1/DEC), skip unit2/FEC
        assert mock_procedures_instance.forecast_for_unit.call_count == 1
        assert len(result) == 2  # 2 groups (1 retrained, 1 skipped)
        
        # Check that unit2/FEC result is marked as skipped
        skipped = [r for r in result if r.get("skipped")]
        assert len(skipped) == 1
        assert skipped[0]["consumer_unit_set_id"] == "unit2"
        assert skipped[0]["indicator"] == "FEC"

    @patch("src.services.retraining_service.TimeSeriesForecastProcedures")
    @patch("src.services.retraining_service.get_client")
    def test_retrain_handles_exception(self, mock_get_client, mock_procedures_class):
        """Test that retrain_for_load handles exceptions gracefully"""
        
        # Setup mock MongoDB client
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        
        # Mock documents
        mock_collection.find.return_value = [
            {"consumer_unit_set_id": "unit1", "indicator_type_code": "DEC", "year": 2020},
        ]
        
        # Mock TimeSeriesForecastProcedures to raise exception
        mock_procedures_instance = MagicMock()
        mock_procedures_class.return_value = mock_procedures_instance
        mock_procedures_instance.forecast_for_unit.side_effect = RuntimeError("Training failed")
        
        # Call retrain_for_load - should not raise, but record error
        result = retrain_for_load("load_123")
        
        # Should have result with error
        assert len(result) == 1
        assert "error" in result[0]
        assert "Training failed" in result[0]["error"]

    @patch("src.services.retraining_service.retrain_for_load")
    @patch("threading.Thread")
    def test_schedule_retraining_creates_thread(self, mock_thread_class, mock_retrain):
        """Test that schedule_retraining spawns a background thread"""
        
        # Mock Thread
        mock_thread_instance = MagicMock()
        mock_thread_class.return_value = mock_thread_instance
        
        # Call schedule_retraining
        result = schedule_retraining("load_123")
        
        # Verify thread was created with correct args
        assert result is True
        mock_thread_class.assert_called_once()
        args, kwargs = mock_thread_class.call_args
        assert kwargs["daemon"] is True
        assert kwargs["target"] == mock_retrain
        assert kwargs["args"] == ("load_123", None)
        
        # Verify thread.start() was called
        mock_thread_instance.start.assert_called_once()


class TestIntegrationScenarios:
    """Integration-style tests for realistic scenarios"""

    @patch("src.services.retraining_service.TimeSeriesForecastProcedures")
    @patch("src.services.retraining_service.get_client")
    @patch("src.services.retraining_service.settings")
    def test_realistic_load_with_multiple_units(self, mock_settings, mock_get_client, mock_procedures_class):
        """Test realistic scenario: load contains data for multiple units and indicators"""
        
        # Setup settings
        mock_settings.mongo_db_name = "tecsys"
        mock_settings.model_retrain_min_new_records = 1
        
        # Setup mock MongoDB client
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        
        # Mock realistic distribution indices data
        mock_collection.find.return_value = [
            {"consumer_unit_set_id": "16648", "indicator_type_code": "DEC", "year": 2024},
            {"consumer_unit_set_id": "16648", "indicator_type_code": "DEC", "year": 2024},  # duplicate year
            {"consumer_unit_set_id": "16648", "indicator_type_code": "FEC", "year": 2024},
            {"consumer_unit_set_id": "16649", "indicator_type_code": "DEC", "year": 2024},
            {"consumer_unit_set_id": "16649", "indicator_type_code": "FEC", "year": 2024},
            {"consumer_unit_set_id": "16649", "indicator_type_code": "FEC", "year": 2024},
        ]
        
        # Mock TimeSeriesForecastProcedures
        mock_procedures_instance = MagicMock()
        mock_procedures_class.return_value = mock_procedures_instance
        mock_procedures_instance.forecast_for_unit.return_value = {
            "success": True,
            "consumer_unit_id": "16648",
            "message": "OK"
        }
        
        # Call retrain_for_load
        result = retrain_for_load("load_abc123")
        
        # Should have 4 groups: (16648, DEC), (16648, FEC), (16649, DEC), (16649, FEC)
        assert len(result) == 4
        
        # All should be successful
        successful = [r for r in result if "error" not in r]
        assert len(successful) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
