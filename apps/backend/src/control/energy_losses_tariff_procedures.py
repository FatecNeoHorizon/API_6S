from pymongo import MongoClient
from src.model import energy_losses_tariff_model
from src.config import parameters
from src.utils.clean_filter import clean_filter, remove_operators_fields
from typing import List
from pydantic import TypeAdapter

class Energy_losses_tariff_procedures():
    connection : None

    def __init__(self):
        self.connection = MongoClient(parameters.mongoDBConnection)

    def insertOne():
        pass

    def getAll(self, filter):
        db = self.connection.zeus

        operators_field = ["process_date"]
        cleaned_dict = clean_filter(filter_dict=filter)
        cleaned_dict = remove_operators_fields(filter_dict=cleaned_dict, fields_array=operators_field)

        cursor = db.energy_losses_tariff.find(cleaned_dict)
        energy_losses_adapter = TypeAdapter(List[energy_losses_tariff_model.EnergyLossesTariff])
        validated_list = energy_losses_adapter.validate_python(cursor)

        self.connection.close()
        return validated_list