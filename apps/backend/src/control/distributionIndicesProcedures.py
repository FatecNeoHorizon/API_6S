from pymongo import MongoClient
from src.model import distributionIndicesModel
from src.config import parameters
from typing import List
from pydantic import TypeAdapter
import json

class DistributionIndicesProcedures():
    connection : None

    def __init__(self):
        self.connection = MongoClient(parameters.mongoDBConnection)

    def insertOne():
        pass

    def getAll(self, filter):
        db = self.connection.zeus
        cursor = db.distribution_indices.find(filter)
        distributionIndicesAdapter = TypeAdapter(List[distributionIndicesModel.DistributionIndices])
        validated_list = distributionIndicesAdapter.validate_python(cursor)
        return validated_list