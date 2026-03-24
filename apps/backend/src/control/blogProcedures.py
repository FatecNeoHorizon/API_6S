from pymongo import MongoClient
from src.model import blogModel
from src.config import parameters
from typing import List
from pydantic import TypeAdapter

class BlogProcedures():
    connection : None

    def __init__(self):
        self.connection = MongoClient(parameters.mongoDBConnection)

    def insertOne():
        pass

    def getAll(self):
        db = self.connection.test
        cursor = db.blog.find()
        blogListAdapter = TypeAdapter(List[blogModel.BlogModel])
        validated_list = blogListAdapter.validate_python(cursor)
        return validated_list