from pymongo import MongoClient
from src.model import energy_losses_tariff_model
from src.config import parameters
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
        cleaned_dict = {key: value for key, value in filter.items() if value is not None}
        cursor = db.energy_losses_tariff.find(cleaned_dict)
        energy_losses_adapter = TypeAdapter(List[energy_losses_tariff_model.EnergyLossesTariff])
        validated_list = energy_losses_adapter.validate_python(cursor)
        return validated_list