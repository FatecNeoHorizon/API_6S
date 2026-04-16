from src.model import blogModel
from src.config.parameters import get_mongo_settings
from src.etl.database import get_client
from typing import List
from pydantic import TypeAdapter

class BlogProcedures():
    connection : None

    def __init__(self):
        _, _, _, _, db_name = get_mongo_settings()
        self.connection = get_client()
        self.db = self.connection[db_name]

    def insertOne():
        pass

    def getAll(self):
        cursor = self.db.blog.find()
        blogListAdapter = TypeAdapter(List[blogModel.BlogModel])
        validated_list = blogListAdapter.validate_python(cursor)
        return validated_list