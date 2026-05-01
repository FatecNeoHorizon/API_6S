import logging
from pathlib import Path
from fastapi import UploadFile
from src.config.settings import Settings
import aiofiles
import magic
import re
import zipfile

logger = logging.getLogger(__name__)

_settings = Settings()
MAX_FILE_SIZE_BYTES = _settings.max_upload_size_mb * 1024 * 1024
STREAM_CHUNK_SIZE_BYTES = 1024 * 1024
MIME_PROBE_SIZE_BYTES = 8192

DYNAMIC_FILE_PATTERNS = {
    r"^indicadores_continuidade_\d{4}_\d{4}$": {
        "extensions": [".csv"],
        "mime_types": ["text/csv", "text/plain", "application/csv"],
    }
}

ALLOWED_FILES = {
    "energy_losses":{
        "extensions": [".xlsx"],
        "mime_types": [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ],
        "required": False,
    },
    "gdb": {
        "extensions": [".zip"],
        "mime_types": ["application/zip", "application/x-zip-compressed","application/octet-stream"],
        "required": False,
    },
    "indicadores_continuidade": {
        "extensions": [".csv"],
        "mime_types": ["text/csv", "text/plain", "application/csv"],
        "required": False,
    },
    "indicadores_continuidade_limite": {
        "extensions": [".csv"],
        "mime_types": ["text/csv", "text/plain", "application/csv"],
        "required": False,
    },
}

def resolve_file_config(file_key: str) -> dict | None:
    if file_key in ALLOWED_FILES:
        return ALLOWED_FILES[file_key]
    for pattern, config in DYNAMIC_FILE_PATTERNS.items():
        if re.match(pattern, file_key):
            return config
    return None

def validate_extensions(filename: str, file_key: str) -> str | None:
    config = resolve_file_config(file_key)
    if not config:
        return f"'{file_key}': tipo de arquivo não permitido."

    expected_ext = config["extensions"]
    actual_ext = Path(filename).suffix.lower()
    if actual_ext not in (expected_ext if isinstance(expected_ext, list) else [expected_ext]):
        return (
            f"'{file_key}': extensão inválida '{actual_ext}'. "
            f"Esperado: '{expected_ext}'."
        )
    return None

def validate_file_size(size: int, file_name: str) -> str | None:
    if size > MAX_FILE_SIZE_BYTES:
        return (
            f"'{file_name}' excede o limite de {_settings.max_upload_size_mb}MB. "
            f"Tamanho recebido: {size / (1024 * 1024):.2f}MB."
        )
    return None

def validate_mime_type(file_bytes: bytes, file_key: str, filename: str) -> str | None:
    config = resolve_file_config(file_key)
    if not config:
        return f"'{file_key}': tipo de arquivo não permitido."

    allowed_mime_types = config["mime_types"]
    detected_mime = magic.from_buffer(file_bytes, mime=True)

    if detected_mime not in allowed_mime_types:
        return (
            f"'{filename}': tipo de conteúdo inválido '{detected_mime}'. "
            f"Tipos permitidos: {allowed_mime_types}."
        )
    return None

def validate_mime_type_from_file(file_path: Path, file_key: str, filename: str) -> str | None:
    config = resolve_file_config(file_key)
    if not config:
        return f"'{file_key}': tipo de arquivo não permitido."

    allowed_mime_types = config["mime_types"]
    detected_mime = magic.from_file(str(file_path), mime=True)

    if detected_mime not in allowed_mime_types:
        return (
            f"'{filename}': tipo de conteúdo inválido '{detected_mime}'. "
            f"Tipos permitidos: {allowed_mime_types}."
        )
    return None

async def validate_and_store_upload(
        upload_file: UploadFile | None,
        file_key: str,
        dest_path: Path,
) -> tuple[Path | None, str | None]:

    if upload_file is None:
        return None, None

    config = resolve_file_config(file_key)
    if config is None:
        return None, f"'{file_key}': tipo de arquivo não reconhecido."

    if error := validate_extensions(upload_file.filename, file_key):
        return None, error

    total_bytes = 0
    mime_probe = bytearray()

    try:
        async with aiofiles.open(dest_path, "wb") as f:
            while True:
                chunk = await upload_file.read(STREAM_CHUNK_SIZE_BYTES)
                if not chunk:
                    break

                total_bytes += len(chunk)
                if error := validate_file_size(total_bytes, upload_file.filename):
                    return None, error

                if len(mime_probe) < MIME_PROBE_SIZE_BYTES:
                    remaining = MIME_PROBE_SIZE_BYTES - len(mime_probe)
                    mime_probe.extend(chunk[:remaining])

                await f.write(chunk)
    finally:
        await upload_file.seek(0)

    if total_bytes == 0:
        return None, f"'{upload_file.filename}': arquivo vazio."

    if mime_probe:
        if error := validate_mime_type(bytes(mime_probe), file_key, upload_file.filename):
            return None, error
    else:
        if error := validate_mime_type_from_file(dest_path, file_key, upload_file.filename):
            return None, error

    if file_key == "gdb":
        if error := validate_gdb_zip_index_from_path(dest_path, upload_file.filename):
            return None, error

    logger.info(
        f"[file_validator] '{upload_file.filename}' validado e persistido com sucesso "
        f"({total_bytes} bytes)."
    )
    return dest_path, None

def validate_gdb_zip_index_from_path(zip_path: Path, filename: str) -> str | None:
    try:
        if not zipfile.is_zipfile(zip_path):
            return "O arquivo 'gdb' não é um ZIP válido."

        with zipfile.ZipFile(zip_path) as zf:
            has_gdb = any(
                ".gdb/" in name.lower() or name.lower().endswith(".gdb")
                for name in zf.namelist()
            )
            if not has_gdb:
                return "O arquivo 'gdb' não contém uma pasta .gdb válida."
    except (zipfile.BadZipFile, OSError, ValueError):
        return f"'{filename}': erro ao validar estrutura do ZIP."

    return None