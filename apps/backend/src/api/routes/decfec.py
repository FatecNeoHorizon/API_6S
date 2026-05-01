from fastapi import APIRouter, HTTPException
from pathlib import Path
from src.etl.load import load_decfec
from src.control import distribution_indices_procedures
from src.etl.extract.extract_limits import extract_limits
from src.etl.extract.extract_decfec import extract_decfec, CHUNK_SIZE
from src.config.settings import Settings

router = APIRouter()
_settings = Settings()

def get_latest_csv_path(pattern: str) -> Path:
    tmp = Path(_settings.tmp_upload_path)
    candidates = list(tmp.rglob(pattern))
    if not candidates:
        raise FileNotFoundError(f"Nenhum arquivo '{pattern}' encontrado no TMP_UPLOAD_PATH.")
    return max(candidates, key=lambda p: p.stat().st_mtime)

@router.get("/process-decfec")
def process_decfec():
    try:
        result = load_decfec()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "message": "DECFEC processado com sucesso",
        **result,
    }

@router.get("/get-dec-fec")
async def get_dec_fec(
    agent_acronym: str | None = None,
    cnpj_number: str | None = None,
    consumer_unit_set_id: str | None = None,
    indicator_type_code: str | None = None,
    year_min: int | None = None,
    period_min: int | None = None,
    year_max: int | None = None,
    period_max: int | None = None
):
    filter_dict = {
        "agent_acronym": agent_acronym,
        "cnpj_number": cnpj_number,
        "consumer_unit_set_id": consumer_unit_set_id,
        "indicator_type_code": indicator_type_code,
        "period": {"$gte": period_min, "$lte": period_max},
        "year": {"$gte": year_min, "$lte": year_max},
    }
    return distribution_indices_procedures.Distribution_indices_procedures().getAll(filter_dict)

@router.get("/test-decfec-file-extraction")
async def test_decfec_file_extraction():
    path = get_latest_csv_path("indicadores-continuidade-coletivos-2020*.csv")
    # Get first chunk and return first 50 rows
    for chunk_df, source_file in extract_decfec(path):
        return {
            "source_file": source_file,
            "sample": chunk_df.head(50).to_dict(orient='records'),
            "total_in_chunk": len(chunk_df),
            "chunk_size_limit": CHUNK_SIZE,
        }

@router.get("/test-limits-file-extraction")
async def test_limits_file_extraction():
    path = get_latest_csv_path("indicadores-continuidade-coletivos-limite*.csv")
    return extract_limits(path)[:50]