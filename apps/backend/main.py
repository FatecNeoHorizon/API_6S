from fastapi import FastAPI

from src.config.middleware import setup_middleware
from src.api.routes import decfec
from src.api.routes import energy_losses
from src.api.routes import network_structure
from src.api.routes import upload
from src.api.routes import users

from src.config.lifespan import lifespan

app = FastAPI(lifespan=lifespan)

setup_middleware(app)
app.include_router(decfec.router)
app.include_router(energy_losses.router)
app.include_router(network_structure.router)
app.include_router(upload.router)
app.include_router(users.router)