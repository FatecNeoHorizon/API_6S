import logging
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from src.control.upload_procedures import managed_upload_dir, process_uploaded_zip
from src.database.connection import get_db
from src.services.upload_service import (
    generate_load_id,
    register_upload_start,
    run_etl_placeholder,
    get_load_history
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/", status_code=202)
async def upload_files(
    background_tasks: BackgroundTasks,
    energy_losses: UploadFile | None = File(default=None),
    gbd: UploadFile | None = File(default=None),
    indicadores_continuidade: UploadFile | None = File(default=None),
    indicadores_continuidade_limite: UploadFile | None = File(default=None),
    ):
    files = {
        "energy_losses": energy_losses,
        "gbd": gbd,
        "indicadores_continuidade": indicadores_continuidade,
        "indicadores_continuidade_limite": indicadores_continuidade_limite,
    }

    db = get_db()
    upload_id = generate_load_id()  # ← só para a pasta temp

    async with managed_upload_dir(upload_id) as upload_dir:
        paths, errors = await process_uploaded_zip(upload_dir, files)

        if errors:
            raise HTTPException(status_code=422, detail=errors)

        load_ids = register_upload_start(db, paths)

        background_tasks.add_task(run_etl_placeholder, db, load_ids, paths)

        logger.info(f"[upload] load_ids {load_ids} registrados. Arquivos: {list(paths.keys())}")

        return {
            "status": "STARTED",
            "arquivos_recebidos": list(paths.keys()),
            "load_ids": load_ids,
        }

@router.get("/status/{load_id}")
def get_upload_status(load_id: str):
    db = get_db()
    load_history = get_load_history(db, load_id)
    
    if not load_history:
        raise HTTPException(status_code=404, detail=f"load_id '{load_id}' não encontrado.")
    
    response = {"load_id": load_id, "status": load_history["status"]}

    if load_history["status"] == "ERROR":
        response["error_message"] = load_history.get("error_message")

    return response