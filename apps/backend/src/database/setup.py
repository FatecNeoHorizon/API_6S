from src.database.connection import get_db
from src.database.collections.energy_losses_tariff import setup_energy_losses_tariff
from src.database.collections.substations import setup_substations
from src.database.collections.distribution_transformers import setup_distribution_transformers
from src.database.collections.conj import setup_conj
from src.database.collections.distribution_indices import setup_distribution_indices
from src.database.collections.load_history import setup_load_history
from src.database.collections.geodatabases import setup_geodatabases
from src.database.collections.predictions import setup_predictions

COLLECTION_SETUPS = [
    ("energy_losses_tariff", setup_energy_losses_tariff),
    ("substations", setup_substations),
    ("distribution_transformers", setup_distribution_transformers),
    ("conj", setup_conj),
    ("distribution_indices", setup_distribution_indices),
    ("load_history", setup_load_history),
    ("geodatabases", setup_geodatabases),
    ("predictions", setup_predictions),
]

def setup():
    db = get_db()
    collections_exist = db.list_collection_names()

    for collection_name, setup_fn in COLLECTION_SETUPS:
        if collection_name == "predictions" or collection_name not in collections_exist:
            setup_fn(db)

    return db