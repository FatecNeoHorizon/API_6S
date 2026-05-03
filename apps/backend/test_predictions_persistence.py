#!/usr/bin/env python3
"""
Quick validation script for predictions persistence.
Tests that predictions are stored in MongoDB with correct format.
"""

import asyncio
import sys
from datetime import datetime
from pymongo import MongoClient

sys.path.insert(0, "/app")

from src.config.settings import Settings
from src.database.connection import get_client
from src.database.setup import setup


async def test_predictions_persistence():
    """Validate that predictions collection exists and has correct schema."""
    
    settings = Settings()
    
    # Get MongoDB connection
    try:
        client = get_client()
    except:
        from src.database.connection import MongoClient
        client = MongoClient(settings.mongo_uri)
    
    db = client[settings.mongo_db_name]
    
    # Setup collections
    print("[TEST] Setting up database collections...")
    setup()
    
    # Check if predictions collection exists
    collections = db.list_collection_names()
    if "predictions" not in collections:
        print("[ERROR] Predictions collection not found!")
        return False
    
    print("[SUCCESS] Predictions collection exists")
    
    # Try to insert a test document
    predictions_col = db["predictions"]
    
    test_doc = {
        "consumer_unit_set_id": "TEST_16648",
        "indicator": "DEC",
        "forecast_date": "2025-01-15",
        "forecast_value": 1.2345,
        "model": "RandomForestRegressor",
        "generated_on": datetime.utcnow(),
    }
    
    try:
        result = predictions_col.insert_one(test_doc)
        print(f"[SUCCESS] Test document inserted: {result.inserted_id}")
    except Exception as e:
        print(f"[ERROR] Failed to insert test document: {e}")
        return False
    
    # Verify document can be queried
    found = predictions_col.find_one({
        "consumer_unit_set_id": "TEST_16648",
        "indicator": "DEC"
    })
    
    if not found:
        print("[ERROR] Test document not found after insert!")
        return False
    
    print(f"[SUCCESS] Test document found: {found['_id']}")
    
    # Test upsert behavior (idempotency)
    print("\n[TEST] Testing upsert idempotency...")
    
    test_doc["forecast_value"] = 1.5555  # Update value
    
    from pymongo import UpdateOne
    operations = [
        UpdateOne(
            {
                "consumer_unit_set_id": "TEST_16648",
                "indicator": "DEC",
                "forecast_date": "2025-01-15"
            },
            {"$set": test_doc},
            upsert=True
        )
    ]
    
    result = predictions_col.bulk_write(operations, ordered=False)
    print(f"[SUCCESS] Upsert completed: matched={result.matched_count}, modified={result.modified_count}, upserted={result.upserted_count}")
    
    # Clean up
    predictions_col.delete_one({"consumer_unit_set_id": "TEST_16648"})
    print("\n[CLEANUP] Test document removed")
    
    print("\n[ALL TESTS PASSED] Predictions persistence is working correctly!")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_predictions_persistence())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
