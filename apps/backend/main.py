from fastapi import FastAPI

from src.control import distribution_indices_procedures
from src.control import energy_losses_tariff_procedures
from src.control import network_structure_procedures
from src.config.middleware import setup_middleware
from src.api.routes import decfec
from src.api.routes import energy_losses
from src.api.routes import network_structure
from src.api.routes import tam_sam
from src.api.routes import upload
from src.api.routes import gdb
from src.api.routes import terms

from src.config.lifespan import lifespan

app = FastAPI(lifespan=lifespan)

setup_middleware(app)

app.include_router(decfec.router)
app.include_router(energy_losses.router)
app.include_router(network_structure.router)
app.include_router(upload.router)
app.include_router(gdb.router)
app.include_router(tam_sam.router)
app.include_router(upload.router)
app.include_router(terms.router)
