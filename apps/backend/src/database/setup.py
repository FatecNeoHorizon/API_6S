from src.etl.database.connection import get_db
from src.etl.database.collections.at_network_segments import setup_at_network_segments
from src.etl.database.collections.consumer_units import setup_consumer_units
from src.etl.database.collections.distribution_indices import setup_distribution_indices
from src.etl.database.collections.distribution_transformers import setup_distribution_transformers
from src.etl.database.collections.domain_indicators import setup_domain_indicators
from src.etl.database.collections.energy_losses_tariff import setup_energy_losses_tariff
from src.etl.database.collections.load_history import setup_load_history
from src.etl.database.collections.mt_network_segments import setup_mt_network_segments
from src.etl.database.collections.municipalities import setup_municipalities
from src.etl.database.collections.substations import setup_substations

COLLECTION_SETUPS = [
    ("at_network_segments",    setup_at_network_segments),
    ("consumer_units",         setup_consumer_units),
    ("distribution_indices",   setup_distribution_indices),
    ("distribution_transformers", setup_distribution_transformers),
    ("domain_indicators",      setup_domain_indicators),
    ("energy_losses_tariff",   setup_energy_losses_tariff),
    ("load_history",           setup_load_history),
    ("mt_network_segments",    setup_mt_network_segments),
    ("municipalities",         setup_municipalities),
    ("substations",            setup_substations),
]

def setup():
    db = get_db()
    collections_exist = db.list_collection_names()

    for collection_name, setup_fn in COLLECTION_SETUPS:
        if collection_name not in collections_exist:
            setup_fn(db)

    return db

if __name__ == "__main__":
    setup()