from fastapi import APIRouter
from src.control import energy_losses_tariff_procedures
from src.etl.extract import extract_energy_losses

router = APIRouter()

@router.get("/get-energy-losses")
async def get_energy_losses(
    distributor: str | None = None,
    distributor_slug: str | None = None,
    state: str | None = None,
    uf: str | None = None,
    process_date_min: str | None = None,
    process_date_max: str | None = None
):
    filter_dict = {
        "distributor": distributor,
        "distributor_slug": distributor_slug,
        "state": state,
        "uf": uf,
        "process_date": {"$gte": process_date_min, "$lte": process_date_max},
    }
    return energy_losses_tariff_procedures.Energy_losses_tariff_procedures().getAll(filter_dict)

@router.get("/test-energy-losses-file-extraction")
async def test_energy_losses_file_extraction():
    return extract_energy_losses.extract_losses()