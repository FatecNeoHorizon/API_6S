import logging
import shutil
from pathlib import Path
from src.config.settings import Settings

from fastapi import UploadFile

from src.utils.file_validator import validate_and_store_upload
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

async def process_uploaded_zip(
        upload_dir: Path,
        files: dict[str, UploadFile | None]
 ) -> tuple[dict[str, Path], list[str]]:

    paths: dict[str, Path] = {}
    errors: list[str] = []

    for file_key, upload_file in files.items():
        if upload_file is None:
            continue

        dest_path = upload_dir / upload_file.filename
        saved_path, error = await validate_and_store_upload(upload_file, file_key, dest_path)

        if error:
            errors.append(error)
            if dest_path.exists():
                dest_path.unlink(missing_ok=True)
            continue

        if saved_path is None:
            continue

        if file_key == "gdb":
            try:
                extract_dir = upload_dir / "gdb_extracted"
                extract_dir.mkdir(exist_ok=True)
                gdb_path = unpack_zip_file(saved_path, extract_dir)
                paths[file_key] = gdb_path
            except Exception as exc:
                errors.append(f"'{upload_file.filename}': falha ao extrair GDB ({exc}).")
                break
        else:
            paths[file_key] = saved_path

    if not paths and not errors:
        errors.append("Nenhum arquivo foi enviado. Envie ao menos um arquivo.")

    if errors:
        cleanup_upload_dir(upload_dir)
        return {}, errors

    logger.info(f"[upload_procedures] Arquivos prontos para ETL: {list(paths.keys())}")
    return paths, []