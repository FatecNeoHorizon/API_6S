from fastapi import APIRouter, Depends
from pymongo.database import Database
from src.database.connection import get_db  # ajuste conforme seu projeto
from src.etl.extract import extract_gdb

router = APIRouter()

@router.get("/test-geodatabase-extraction")
async def test_geodatabase_extraction(db: Database = Depends(get_db)):
    return extract_gdb.extract_gdb(db)