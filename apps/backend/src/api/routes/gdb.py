from fastapi import APIRouter, Depends
from pymongo.database import Database
from pathlib import Path
from src.database.connection import get_db
from src.etl.extract.gdb_orchestrator import run_extraction, extract_gdb_preview
from src.services.upload_service import generate_load_id
from src.config.settings import Settings
from src.repositories.load_history_repository import insert_load_history
from src.services.upload_service import generate_load_id, build_load_document
router = APIRouter()
_settings = Settings()

def get_latest_gdb_path() -> Path:
    tmp = Path(_settings.tmp_upload_path)
    candidates = list(tmp.rglob("*.gdb"))
    if not candidates:
        raise FileNotFoundError("Nenhum arquivo .gdb encontrado no TMP_UPLOAD_PATH.")
    return max(candidates, key=lambda p: p.stat().st_mtime)

@router.get("/test-geodatabase-extraction")
async def test_geodatabase_extraction(db: Database = Depends(get_db)):
    path = get_latest_gdb_path()
    load_id = generate_load_id()
    insert_load_history(db, build_load_document(load_id, "gdb", source_file=str(path)))
    run_extraction(db, path, load_id)
    return extract_gdb_preview(path) 