from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone
import json

from src.model import blogModel
from src.procedures import blogProcedures

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/dict-to-json")
async def dict_to_json():
    dict_thing = {"message": "Hello World"}
    return_json = json.dumps(dict_thing)
    return return_json

@app.get("/items/{item_id}")
async def read_item(item_id : int):
    return {"item_id": item_id}

@app.get("/fake-items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

@app.post("/create-items/")
async def create_item(item: Item):
    return item

@app.post("/create-import-test")
async def create_import_test(item: blogModel.BlogModel):
    return item

@app.get("/get-import-test",response_model=blogModel.BlogModel)
async def get_all_blogs():
    idk = blogModel.BlogModel()
    idk.content = 'IHHH DEU BAO'
    return idk

@app.get("/get-all-blogs")
async def get_all_blogs():
    returnThing = blogProcedures.BlogProcedures().getAll()
    return returnThing