from pymongo import MongoClient
from src.config.settings import Settings

settings = Settings()

_client: MongoClient | None = None

def get_client() -> MongoClient:
    if _client is None:
        raise RuntimeError("MongoDB client not initialized. Check lifespan setup.")
    return _client

def get_db():
    return get_client()[settings.mongo_db_name]