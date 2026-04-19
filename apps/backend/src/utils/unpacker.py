import zipfile
import logging
from pathlib import Path
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def unpack_zip_file(zip_path: Path, extract_to: Path) -> Path:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            if ".." in member or member.startswith("/"):
                raise HTTPException(
                    status_code=422,
                    detail="O arquivo Zip contém caminhos inválidos ou inseguros (possível path traversal)."
                )
        zip_ref.extractall(extract_to)

    zip_dirs = [dir for dir in extract_to.rglob("*.gbd") if dir.is_dir()]
    if not zip_dirs:
        raise HTTPException(
            status_code=422,
            detail="O arquivo Zip não contém um diretório com extensão .gbd."
        )
    
    zip_path = zip_dirs[0]
    logger.info(f"Arquivo Zip descompactado com sucesso: {zip_path}")
    return zip_path