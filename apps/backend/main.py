from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.config.middleware import setup_middleware
from src.config.validation import format_validation_errors
from src.config.exception_handlers import (
    unhandled_exception_handler,
    validation_exception_handler,
)
from src.api.routes import decfec
from src.api.routes import energy_losses
from src.api.routes import network_structure
from src.api.routes import tam_sam
from src.api.routes import upload
from src.api.routes import gdb
from src.api.routes import users
from src.api.routes import auth
from src.api.routes import consent
from src.api.routes import terms
from src.api.routes import admin_terms

from src.config.lifespan import lifespan

app = FastAPI(lifespan=lifespan)

setup_middleware(app)

app.include_router(decfec.router)
app.include_router(energy_losses.router)
app.include_router(network_structure.router)
app.include_router(upload.router)
app.include_router(gdb.router)
app.include_router(tam_sam.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(consent.router)
app.include_router(terms.router)
app.include_router(admin_terms.router)

app.add_exception_handler(Exception, unhandled_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)