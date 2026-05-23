from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.config.middleware import setup_middleware
from src.config.exception_handlers import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from src.config.rate_limiter import limiter
from src.api.routes import decfec
from src.api.routes import energy_losses
from src.api.routes import network_structure
from src.api.routes import tam_sam
from src.api.routes import timeseries
from src.api.routes import upload
from src.api.routes import gdb
from src.api.routes import geo
from src.api.routes import users
from src.api.routes import auth
from src.api.routes import consent
from src.api.routes import terms
from src.api.routes import admin_terms
from src.api.routes import predictions
from src.api.routes import incident_notification

from src.config.lifespan import lifespan

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter

setup_middleware(app)


def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "too_many_requests", "message": f"Rate limit exceeded: {exc.detail}"},
    )


app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

app.include_router(decfec.router)
app.include_router(energy_losses.router)
app.include_router(network_structure.router)
app.include_router(upload.router)
app.include_router(gdb.router)
app.include_router(geo.router, prefix="/geo")
app.include_router(tam_sam.router)
app.include_router(timeseries.router)
app.include_router(predictions.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(consent.router)
app.include_router(terms.router)
app.include_router(admin_terms.router)
app.include_router(incident_notification.router)

app.add_exception_handler(Exception, unhandled_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
