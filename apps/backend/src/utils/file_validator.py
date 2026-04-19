import logging
from pathlib import Path
from fastapi import UploadFile
import magic
import re

logger = logging.getLogger(__name__)

MAX_FILE_SIZE_MB = 500
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

DYNAMIC_FILE_PATTERNS = {
    r"^indicadores_continuidade_\d{4}_\d{4}$": {
        "extensions": ".csv",
        "mime_types": ["text/csv", "text/plain", "application/csv"],
    }
}

ALLOWED_FILES = {
    "energy_losses":{
        "extensions": ".xlsx",
        "mime_types": [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ],
        "required": False,
    },
    "gbd": {
        "extensions": [".zip", ".rar", ".7z", ".gz", ".tar", ".bz2", ".z"],
        "mime_types": [
            "application/zip",
            "application/x-rar-compressed",
            "application/x-7z-compressed",
            "application/gzip",
            "application/x-tar",
            "application/x-bzip2",
            "application/x-compress"
        ],
        "required": False,

    },
    "indicadores_continuidade": {
        "extensions": ".csv",
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

def validate_file_size(file_bytes: bytes, file_name: str) -> str | None:
    size = len(file_bytes)
    if size > MAX_FILE_SIZE_BYTES:
        return (
            f"'{file_name}' excede o limite de {MAX_FILE_SIZE_MB}MB. "
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

async def validate_and_read(
        upload_file: UploadFile | None,
        file_key: str
) -> tuple[bytes | None, str | None]:
    if upload_file is None:
        return None, None
    
    config = resolve_file_config(file_key)

    if config is None:
        return None, f"'{file_key}': tipo de arquivo não reconhecido."

    if error := validate_extensions(upload_file.filename, file_key):
        return None, error

    file_bytes = await upload_file.read() 

    if error := validate_file_size(file_bytes, upload_file.filename):
        return None, error
    
    if error := validate_mime_type(file_bytes, file_key, upload_file.filename):
        return None, error
    
    logger.info(f"[file_validator] '{upload_file.filename}' validado com sucesso.")
    return file_bytes, None

async def validate_all_files(
        files: dict[str, UploadFile | None],
) -> tuple[dict[str, bytes], list[str]]:
    
    validated: dict[str, bytes] = {}
    errors: list[str] = []

    for file_key, upload_file in files.items():
        file_bytes, error = await validate_and_read(upload_file, file_key)
        if error:
            errors.append(error)
        elif file_bytes is not None:
            validated[file_key] = file_bytes
    
    if not validated and not errors:
        errors.append("Nenhum arquivo foi enviado. Envie ao menos um arquivo.")
        logger.error("[file_validator] Nenhum arquivo recebido.")

    return validated, errors