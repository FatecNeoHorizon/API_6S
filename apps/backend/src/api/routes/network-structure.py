from fastapi import FastAPI, HTTPException
from src.control import network_structure_procedures


@app.get("/network-structure/summary")
async def get_summary():
    return network_structure_procedures.NetworkStructureProcedures().get_summary()

@app.get("/network-structure/assets")
async def get_assets(region: str | None = None, type: str | None = None, status: str | None = None):
    return network_structure_procedures.NetworkStructureProcedures().get_assets(region, type, status)

@app.get("/network-structure/transformer/{transformer_id}")
async def get_transformer_detail(transformer_id: str):
    return network_structure_procedures.NetworkStructureProcedures().get_transformer_detail(transformer_id)

@app.get("/network-structure/substation/{substation_id}")
async def get_substation_detail(substation_id: str):
    return network_structure_procedures.NetworkStructureProcedures().get_substation_detail(substation_id)