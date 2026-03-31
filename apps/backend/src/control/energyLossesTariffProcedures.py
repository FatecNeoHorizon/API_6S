from pymongo import MongoClient
from src.model import energyLossesTariffModel
from src.config import parameters
from typing import List
from pydantic import TypeAdapter

class EnergyLossesTariffProcedures():
    connection : None

    def __init__(self):
        self.connection = MongoClient(parameters.mongoDBConnection)

    def insertOne():
        pass

    def getAll(self, filter):
        db = self.connection.zeus
        cursor = db.energy_losses_tariff.find(filter)
        energyLossesAdapter = TypeAdapter(List[energyLossesTariffModel.EnergyLossesTariff])
        validated_list = energyLossesAdapter.validate_python(cursor)
        return validated_list