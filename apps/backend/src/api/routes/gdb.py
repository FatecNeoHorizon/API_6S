from fastapi import APIRouter
from src.control import energy_losses_tariff_procedures
from src.etl.extract import extract_gdb

router = APIRouter()

@router.get("/test-geodatabase-extraction")
async def test_geodatabase_extraction():
    return extract_gdb.extract_gdb()