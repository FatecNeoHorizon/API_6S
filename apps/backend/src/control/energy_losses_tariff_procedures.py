from src.model import energy_losses_tariff_model
from src.config.parameters import get_mongo_settings
from src.etl.database import get_client
from src.utils.clean_filter import clean_filter, remove_operators_fields
from typing import List
from pydantic import TypeAdapter

class Energy_losses_tariff_procedures():
    connection : None

    def __init__(self):
        _, _, _, _, db_name = get_mongo_settings()
        self.connection = get_client()
        self.db = self.connection[db_name]

    def insertOne():
        pass

    def getAll(self, filter):
        operators_field = ["process_date"]
        cleaned_dict = clean_filter(filter_dict=filter)
        cleaned_dict = remove_operators_fields(filter_dict=cleaned_dict, fields_array=operators_field)

        cursor = self.db.energy_losses_tariff.find(cleaned_dict)
        energy_losses_adapter = TypeAdapter(List[energy_losses_tariff_model.EnergyLossesTariff])
        validated_list = energy_losses_adapter.validate_python(cursor)

        self.connection.close()
        return validated_list