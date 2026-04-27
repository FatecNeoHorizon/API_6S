from contextlib import asynccontextmanager

import pymongo
from fastapi import FastAPI

from src.config.settings import Settings
from src.config.logger import configure_logging 
from src.database.connection import get_db
from src.database.setup import setup
from src.database import connection
from src.database.postgres import init_postgres_pool, close_postgres_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings = Settings()
        
    mongo_client = pymongo.MongoClient(
        settings.mongo_uri,
        maxPoolSize=settings.mongo_max_pool_size,
        serverSelectionTimeoutMS=settings.mongo_server_selection_timeout_ms,
        connectTimeoutMS=settings.mongo_connect_timeout_ms,
    )

    app.mongodb = mongo_client
    connection._client = mongo_client

    init_postgres_pool()

    setup()

    yield

    close_postgres_pool()

    connection._client = None

    if hasattr(app, "mongodb") and app.mongodb:
        app.mongodb.close()
        delattr(app, 'mongodb')
    
    # Clean up the get_db function reference
    if hasattr(get_db, '_client'):
        delattr(get_db, '_client')
