from fastapi import APIRouter, Query
from src.control import network_structure_procedures

router = APIRouter(prefix="/network-structure")

@router.get("/summary")
async def get_summary():
    return network_structure_procedures.NetworkStructureProcedures().get_summary()

@router.get("/assets")
async def get_assets(
    region: str | None = None,
    type: str | None = None,
    status: str | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
):
    return network_structure_procedures.NetworkStructureProcedures().get_assets(
        region, type, status, search, page, page_size
    )

@router.get("/transformer/{transformer_id}")
async def get_transformer_detail(transformer_id: str):
    return network_structure_procedures.NetworkStructureProcedures().get_transformer_detail(transformer_id)

@router.get("/substation/{substation_id}")
async def get_substation_detail(substation_id: str):
    return network_structure_procedures.NetworkStructureProcedures().get_substation_detail(substation_id)