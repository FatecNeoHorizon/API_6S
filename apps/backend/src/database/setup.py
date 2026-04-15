from src.database.client import get_client
from src.config.parameters import get_mongo_settings
from src.database.collections import (
    domain_indicators,
    distribution_indices,
    energy_losses_tariff,
    consumer_units_pj,
    mt_network_segments,
    at_network_segments,
    substations,
    distribution_transformers,
    municipalities,
    load_history,
)

def setup():
    _, _, _, _, mongo_db = get_mongo_settings()
    db = get_client()[mongo_db]

    domain_indicators.create(db)
    distribution_indices.create(db)
    energy_losses_tariff.create(db)
    consumer_units_pj.create(db)
    mt_network_segments.create(db)
    at_network_segments.create(db)
    substations.create(db)
    distribution_transformers.create(db)
    municipalities.create(db)
    load_history.create(db)

    return db

if __name__ == "__main__":
    setup()