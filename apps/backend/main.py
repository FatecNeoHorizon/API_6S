from src.etl.load_decfec import load_decfec
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.control import distribution_indices_procedures
from src.control import energy_losses_tariff_procedures
from src.control import network_structure_procedures
from src.config.middleware import setup_middleware
from src.api.routes import decfec
from src.api.routes import energy_losses
from src.api.routes import network_structure
from src.api.routes import upload
from src.api.routes import gdb

from contextlib import asynccontextmanager
from src.etl.database import setup

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup()
    from src.model.seed import seed
    seed()
    yield

app = FastAPI(lifespan=lifespan)

setup_middleware(app)
app.include_router(decfec.router)
app.include_router(energy_losses.router)
app.include_router(network_structure.router)
app.include_router(upload.router)
app.include_router(gdb.router)
