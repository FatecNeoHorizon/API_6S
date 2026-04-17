from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.database.setup import setup
from src.core.middleware import setup_middleware
from src.routes import decfec, energy_losses, network_structure

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