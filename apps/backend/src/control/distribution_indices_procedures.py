from src.model import distribution_indices_model
from src.config.settings import Settings
from src.database.connection import get_client
from src.utils.clean_filter import clean_filter, remove_operators_fields
from typing import List, Optional
from pydantic import TypeAdapter
import pymongo

# Get settings for database name
_settings = Settings()

class Distribution_indices_procedures():
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
            # Use provided connection (from app.mongodb - preferred)
            self.connection = connection
        else:
            # Fallback: create new connection (for backward compatibility)
            self.connection = get_client()
        
        self.db = self.connection[_settings.mongo_db_name]

    def insertOne(self):
        pass

    def getAll(self, filter):
        operators_field = ["period", "year"]
        cleaned_dict = clean_filter(filter_dict=filter)
        cleaned_dict = remove_operators_fields(filter_dict=cleaned_dict, fields_array=operators_field)

        cursor = self.db.distribution_indices.find(cleaned_dict)
        distribution_indices_adapter = TypeAdapter(List[distribution_indices_model.DistributionIndices])
        validated_list = distribution_indices_adapter.validate_python(cursor)

        # NOTE: Do NOT close the connection here.
        # If using app.mongodb (shared pool), closing prematurely destroys the connection.
        # The connection is managed by the app lifespan and closed on shutdown.
        # Only close if this instance created its own connection (backward compat).
        
        return validated_list