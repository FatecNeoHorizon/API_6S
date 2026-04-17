from src.model import distribution_indices_model
from src.config.parameters import get_mongo_settings
from src.etl.database import get_client
from src.utils.clean_filter import clean_filter, remove_operators_fields
from typing import List
from pydantic import TypeAdapter

class Distribution_indices_procedures():
    connection : None

    def __init__(self):
        _, _, _, _, db_name = get_mongo_settings()
        self.connection = get_client()
        self.db = self.connection[db_name]

    def insertOne():
        pass

    def getAll(self, filter):
        operators_field = ["period", "year"]
        cleaned_dict = clean_filter(filter_dict=filter)
        cleaned_dict = remove_operators_fields(filter_dict=cleaned_dict, fields_array=operators_field)

        cursor = self.db.distribution_indices.find(cleaned_dict)
        distribution_indices_adapter = TypeAdapter(List[distribution_indices_model.DistributionIndices])
        validated_list = distribution_indices_adapter.validate_python(cursor)

        self.connection.close()
        return validated_list