from fastapi import APIRouter, HTTPException
from apps.backend.src.etl.load.load_decfec import load_decfec
from src.control import distribution_indices_procedures

router = APIRouter()

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