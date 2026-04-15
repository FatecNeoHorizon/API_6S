from pymongo import MongoClient
from src.config.parameters import get_mongo_settings, get_mongo_uri

def get_client():
    return MongoClient(get_mongo_uri())