from pymongo import MongoClient
from src.model import distribution_indices_model
from src.config import parameters
from typing import List
from pydantic import TypeAdapter

class Distribution_indices_procedures():
    connection : None

    def __init__(self):
        self.connection = MongoClient(parameters.mongoDBConnection)

    def insertOne():
        pass

    def getAll(self, filter):
        db = self.connection.zeus
        cleaned_dict = {key: value for key, value in filter.items() if value is not None}
        cursor = db.distribution_indices.find(cleaned_dict)
        distribution_indices_adapter = TypeAdapter(List[distribution_indices_model.DistributionIndices])
        validated_list = distribution_indices_adapter.validate_python(cursor)
        return validated_list