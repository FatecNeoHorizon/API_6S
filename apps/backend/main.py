from src.etl.get_decfec_file import get_filepath
from src.etl.load_decfec import load_decfec
from src.etl.load_ucbt import load_ucbt_tab
from fastapi import FastAPI, HTTPException

from src.control import distribution_indices_procedures
from src.control import energy_losses_tariff_procedures
from src.control import blogProcedures
from src.model import blogModel

from contextlib import asynccontextmanager
from src.etl.database import setup

@asynccontextmanager
async def lifespan(app: FastAPI):
    import os
    setup()
    yield

app = FastAPI(lifespan=lifespan)

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/")
async def root():
    return {"message": "Exemplo GET simples"}

@app.get("/exemplo-parametro-path/{path_id}")
async def read_item(path_id : int):
    return {"path_id": path_id}

@app.get("/exemplo-skip-limit/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

@app.post("/exemplo-post-body-schema")
async def create_import_test(item: blogModel.BlogModel):
    return item

@app.get("/exemplo-get-retorno-schema",response_model=blogModel.BlogModel)
async def get_all_blogs():
    idk = blogModel.BlogModel()
    idk.content = 'IHHH DEU BAO'
    return idk

@app.get("/exemplo-mongodb")
async def get_all_blogs():
    returnThing = blogProcedures.BlogProcedures().getAll()
    return returnThing

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
                      indicator_type_code : str | None = None, year: int | None = None, period : int | None = None):
    filterDict = {
        "agent_acronym" : agent_acronym,
        "cnpj_number" : cnpj_number,
        "consumer_unit_set_id" : consumer_unit_set_id,
        "indicator_type_code" : indicator_type_code,
        "year" : year,
        "period" : period
    }
    
    returnThing = distribution_indices_procedures.Distribution_indices_procedures().getAll(filterDict)
    return returnThing

@app.get("/get-energy-losses")
async def get_energy_losses(distributor: str | None = None, distributor_slug: str | None = None, state: str | None = None, 
                      uf : str | None = None, process_date: str | None = None):
    filterDict = {
        "distributor" : distributor,
        "distributor_slug" : distributor_slug,
        "state" : state,
        "uf" : uf,
        "process_date" : process_date,
    }
    
    returnThing = energy_losses_tariff_procedures.Energy_losses_tariff_procedures().getAll(filterDict)
    return returnThing
