from fastapi import FastAPI
import pymongo

from src.config.settings import Settings
from src.config.middleware import setup_middleware
from src.database.connection import get_db

from contextlib import asynccontextmanager
from src.database.setup import setup

from src.api.routes import decfec
from src.api.routes import energy_losses
from src.api.routes import network_structure

from src.config.lifespan import lifespan
from src.config.settings import Settings

app = FastAPI(lifespan=lifespan)

setup_middleware(app)
app.include_router(decfec.router)
app.include_router(energy_losses.router)
app.include_router(network_structure.router)