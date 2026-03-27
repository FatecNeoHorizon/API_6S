from fastapi import FastAPI
from pydantic import BaseModel

from src.model import blogModel
from src.control import blogProcedures

from contextlib import asynccontextmanager
from src.etl.database import setup

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup()
    yield

app = FastAPI(lifespan=lifespan)

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

app = FastAPI()

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