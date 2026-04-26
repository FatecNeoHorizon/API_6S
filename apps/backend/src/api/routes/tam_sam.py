from fastapi import APIRouter, HTTPException

from src.control.tam_sam_procedures import Tam_sam_procedures

router = APIRouter(prefix="/tam-sam", tags=["tam_sam"])


@router.post("/calculate")
async def calculate_tam_total():
    return Tam_sam_procedures().calculate_and_persist_tam_total()


@router.get("/")
async def get_tam_total():
    result = Tam_sam_procedures().get_tam_total()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="TAM ainda nao calculado. Execute POST /tam-sam/calculate primeiro.",
        )

    return result
