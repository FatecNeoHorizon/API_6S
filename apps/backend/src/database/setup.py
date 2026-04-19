from src.database.connection import get_db
from src.database.collections.at_network_segments import setup_at_network_segments
from src.database.collections.consumer_units_pj import setup_consumer_units_pj
from src.database.collections.distribution_indices import setup_distribution_indices
from src.database.collections.distribution_transformers import setup_distribution_transformers
from src.database.collections.domain_indicators import setup_domain_indicators
from src.database.collections.energy_losses_tariff import setup_energy_losses_tariff
from src.database.collections.load_history import setup_load_history
from src.database.collections.mt_network_segments import setup_mt_network_segments
from src.database.collections.municipalities import setup_municipalities
from src.database.collections.substations import setup_substations

COLLECTION_SETUPS = [
    ("at_network_segments",    setup_at_network_segments),
    ("consumer_units_pj",      setup_consumer_units_pj),
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