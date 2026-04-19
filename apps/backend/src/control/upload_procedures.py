import logging
import uuid
import shutil
import aiofiles
from pathlib import Path
from contextlib import asynccontextmanager
from src.config.settings import Settings

from fastapi import UploadFile
import magic

from src.utils.file_validator import validate_all_files
from src.utils.unpacker import unpack_zip_file

_settings = Settings()

logger = logging.getLogger(__name__)

UPLOAD_BASE_DIR = Path(_settings.tmp_upload_path)

def create_upload_dir(load_id: str) -> Path:
    upload_dir = UPLOAD_BASE_DIR / load_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"[upload_procedures] Pasta temporária criada: {upload_dir}")
    return upload_dir

def cleanup_upload_dir(upload_dir: Path) -> None:
    if upload_dir.exists():
        shutil.rmtree(upload_dir)
        logger.info(f"[upload_procedures] Pasta temporária removida: {upload_dir}")

@asynccontextmanager
async def managed_upload_dir(load_id: str):
    upload_dir = create_upload_dir(load_id)
    try:
        yield upload_dir
    finally:
        cleanup_upload_dir(upload_dir)

async def save_file(file_bytes: bytes, dest_path: Path) -> None:
    async with aiofiles.open(dest_path, 'wb') as f:
        await f.write(file_bytes)
    logger.info(f"[upload_procedures] Arquivo salvo: {dest_path} ({len(file_bytes)} bytes)")

async def process_uploaded_zip(
        upload_dir: Path,
        files: dict[str, UploadFile | None]
 ) -> tuple[dict[str, Path], list[str]]:
    
    validated, erros = await validate_all_files(files)

    if erros:
        return {}, erros
    
    paths: dict[str, Path] = {}

    for file_key, (file_bytes, original_filename) in validated.items():
        dest_path = upload_dir / original_filename
        await save_file(file_bytes, dest_path)

        if file_key == "gbd":
            extract_dir = upload_dir / "gbd_extracted"
            extract_dir.mkdir()
            gdb_path = unpack_zip_file(dest_path, extract_dir)
            paths[file_key] = gdb_path
        else:
            paths[file_key] = dest_path
    
    logger.info(f"[upload_procedures] Arquivos prontos para ETL: {list(paths.keys())}")
    return paths, []

def _resolve_extension(file_key: str, file_bytes: bytes) -> str:

    detected_mime = magic.from_buffer(file_bytes, mime=True)

    mime_to_ext = {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
        "text/csv": ".csv",
        "text/plain": ".csv",
        "application/csv": ".csv",
        "application/zip": ".zip",
        "application/x-rar-compressed": ".rar",
        "application/x-7z-compressed": ".7z",
        "application/gzip": ".gz",
        "application/x-tar": ".tar",
        "application/x-bzip2": ".bz2",
        "application/x-compress": ".z",
    }

    return mime_to_ext.get(detected_mime, "")