from typing import Literal

from fastapi import APIRouter, HTTPException, Depends, Query

from src.api.schemas.response import success_response
from src.control.tam_sam_procedures import Tam_sam_procedures
from src.api.dependencies.auth import AuthenticatedUser, require_admin, get_current_user

router = APIRouter(prefix="/tam-sam", tags=["tam_sam"])


@router.post("/calculate")
async def calculate_tam_total(admin: AuthenticatedUser = Depends(require_admin) ):
    return success_response(Tam_sam_procedures().calculate_and_persist_tam_total())


@router.get("/tam")
async def get_tam_total(current_user: AuthenticatedUser = Depends(get_current_user)):
    result = Tam_sam_procedures().get_tam_total()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="TAM ainda nao calculado. Execute POST /tam-sam/calculate primeiro.",
        )

    return success_response(result)

@router.get("/sam")
async def get_sam_total(
    year: int,
    indicator: Literal["DEC", "FEC"] = Query(
        ...,
        description="Indicador usado para avaliar elegibilidade no SAM.",
    ),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    
    result = Tam_sam_procedures().get_sam_total(year, indicator)

    return success_response({"sam_total": result, "year": year, "indicator": indicator})

@router.get("/sam-top-ten")
async def get_sam_top_ten(year: int, indicator_type_code: str, current_user: AuthenticatedUser = Depends(get_current_user)):
    
    result = Tam_sam_procedures().get_sam_top_ten(year, indicator_type_code)

    return success_response(result)
