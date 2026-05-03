import logging
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from src.control.upload_procedures import process_uploaded_zip, create_upload_dir
from src.database.connection import get_db
from src.services.upload_service import (
    generate_load_id,
    register_upload_start,
    run_etl,
    get_upload_status as fetch_upload_status,
    get_batch_status as fetch_batch_status,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/", status_code=202)
async def upload_files(
    background_tasks: BackgroundTasks,
    energy_losses: UploadFile | None = File(default=None),
    gdb: UploadFile | None = File(default=None),
    indicadores_continuidade: UploadFile | None = File(default=None),
    indicadores_continuidade_limite: UploadFile | None = File(default=None),
    ):
    files = {
        "energy_losses": energy_losses,
        "gdb": gdb,
        "indicadores_continuidade": indicadores_continuidade,
        "indicadores_continuidade_limite": indicadores_continuidade_limite,
    }

    db = get_db()
    batch_id  = generate_load_id()    
    upload_dir = create_upload_dir(batch_id)

    paths, errors = await process_uploaded_zip(upload_dir, files)

    if errors:
        raise HTTPException(status_code=422, detail=errors)

    load_ids = register_upload_start(db, paths, batch_id=batch_id)

    background_tasks.add_task(run_etl, db, load_ids, paths, upload_dir)

    logger.info(f"[upload] load_ids {load_ids} registrados. Arquivos: {list(paths.keys())}")

    return {
        "status": "STARTED",
        "batch_id": batch_id,
        "arquivos_recebidos": list(paths.keys()),
        "load_ids": load_ids,
        }

@router.get("/batch/{batch_id}")
def get_batch_status(batch_id: str):
    db = get_db()
    result = fetch_batch_status(db, batch_id)

    if not result:
        raise HTTPException(status_code=404, detail=f"batch_id '{batch_id}' não encontrado.")

    return result