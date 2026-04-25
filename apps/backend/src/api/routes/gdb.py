from src.etl.extract.gdb_orchestrator import run_extraction
from fastapi import APIRouter, Depends
from pymongo.database import Database
from src.database.connection import get_db
from src.etl.extract.gdb_orchestrator import run_extraction

router = APIRouter()

@router.get("/test-geodatabase-extraction")
async def test_geodatabase_extraction(db: Database = Depends(get_db)):
    return run_extraction(db)