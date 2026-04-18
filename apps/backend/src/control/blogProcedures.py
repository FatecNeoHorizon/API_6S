from src.model import blogModel
from src.config.settings import Settings
from src.etl.database import get_client
from typing import List, Optional
from pydantic import TypeAdapter
import pymongo

# Get settings for database name
_settings = Settings()

class BlogProcedures():
    connection: Optional[pymongo.MongoClient]
    db: Optional[pymongo.database.Database]

    def __init__(self, connection: Optional[pymongo.MongoClient] = None):
        """
        Initialize procedures with optional MongoDB connection.
        
        Args:
            connection: MongoDB client instance. If not provided, a new connection is created.
                       Prefer to pass the shared connection from app.mongodb to reuse the pool.
        """
        if connection is not None:
            self.connection = connection
        else:
            # Fallback: create new connection (for backward compatibility)
            self.connection = get_client()
        
        self.db = self.connection[_settings.mongo_db_name]

    def insertOne():
        pass

    def getAll(self):
        cursor = self.db.blog.find()
        blogListAdapter = TypeAdapter(List[blogModel.BlogModel])
        validated_list = blogListAdapter.validate_python(cursor)
        return validated_list