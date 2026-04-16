from pymongo import MongoClient
from src.config.parameters import get_mongo_uri,get_mongo_settings

def get_client() -> MongoClient:
    return MongoClient(get_mongo_uri())

def get_db():
    client = get_client()
    _, _, _, _, mongo_db = get_mongo_settings()
    return client[mongo_db]