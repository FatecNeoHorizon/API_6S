import zipfile
import io
from pathlib import Path

def unpack_zip_file(zip_path: Path, extract_dir: Path) -> Path:
    # mantém para outros usos eventuais
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extract_dir)
    return _find_gdb(extract_dir)

def unpack_zip_from_bytes(file_bytes: bytes, extract_dir: Path) -> Path:
    with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
        zf.extractall(extract_dir)
    return _find_gdb(extract_dir)

def _find_gdb(extract_dir: Path) -> Path:
    candidates = [p for p in extract_dir.rglob("*.gdb") if p.is_dir()]
    if not candidates:
        raise ValueError("Nenhuma pasta .gdb encontrada após extração.")
    return candidates[0]