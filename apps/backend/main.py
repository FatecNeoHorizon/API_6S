from src.etl.get_decfec_file import get_filepath
from src.etl.load_decfec import load_decfec
from src.etl.load_ucbt import load_ucbt_tab
from fastapi import FastAPI, HTTPException

from src.control import distribution_indices_procedures
from src.control import energy_losses_tariff_procedures
from src.control import blogProcedures
from src.model import blogModel
from src.control import network_structure_procedures

from contextlib import asynccontextmanager
from src.etl.database import setup

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup()
    from src.model.seed import seed
    seed()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/process-csv")
def process_csv():
    result = load_decfec()

    if not result:
        return {"message": "Nenhum registro inserido"}

    return {"message": "CSV processado com sucesso", "inserted_lines": len(result)}


@app.get("/process-ucbt")
def process_ucbt(file_path: str | None = None, chunk_size: int = 100000):
    try:
        result = load_ucbt_tab(file_path=file_path, chunk_size=chunk_size)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "message": "UCBT processado com sucesso",
        **result,
    }


@app.get("/get-dec-fec")
async def get_dec_fec(agent_acronym: str | None = None, cnpj_number: str | None = None, consumer_unit_set_id: str | None = None, 
                      indicator_type_code : str | None = None, year_min: int | None = None, period_min : int | None = None,
                      year_max: int | None = None, period_max: int | None = None):
    
    filterDict = {
        "agent_acronym" : agent_acronym,
        "cnpj_number" : cnpj_number,
        "consumer_unit_set_id" : consumer_unit_set_id,
        "indicator_type_code" : indicator_type_code,
        "period" : {"$gte" : period_min,
                    "$lte" : period_max},
        "year" : {"$gte" : year_min,
                  "$lte" : year_max}
    }

    returnThing = distribution_indices_procedures.Distribution_indices_procedures().getAll(filterDict)
    return returnThing

@app.get("/get-energy-losses")
async def get_energy_losses(distributor: str | None = None, distributor_slug: str | None = None, state: str | None = None, 
                      uf : str | None = None, process_date_min: str | None = None, process_date_max: str | None = None):
    filterDict = {
        "distributor" : distributor,
        "distributor_slug" : distributor_slug,
        "state" : state,
        "uf" : uf,
        "process_date" : {"$gte" : process_date_min,
                "$lte" : process_date_max},
    }
    
    returnThing = energy_losses_tariff_procedures.Energy_losses_tariff_procedures().getAll(filterDict)
    return returnThing

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