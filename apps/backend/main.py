from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.database.setup import setup
from src.config.middleware import setup_middleware
from src.api.routes import decfec
from src.api.routes import energy_losses
from src.api.routes import network_structure

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