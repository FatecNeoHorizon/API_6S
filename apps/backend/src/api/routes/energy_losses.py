from fastapi import APIRouter
from pathlib import Path
from src.control import energy_losses_tariff_procedures
from src.etl.extract.extract_energy_losses import extract_losses_preview
from src.config.settings import Settings

router = APIRouter()
_settings = Settings()

def get_latest_xlsx_path() -> Path:
    tmp = Path(_settings.tmp_upload_path)
    candidates = list(tmp.rglob("*.xlsx"))
    if not candidates:
        raise FileNotFoundError("Nenhum arquivo .xlsx encontrado no TMP_UPLOAD_PATH.")
    return max(candidates, key=lambda p: p.stat().st_mtime)

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
    path = get_latest_xlsx_path()
    return extract_losses_preview(path, limit=50)