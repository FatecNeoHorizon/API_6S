from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import Settings
from src.config.pending_consent_middleware import PendingConsentMiddleware
from src.config.logging_middleware import LoggingMiddleware

def setup_middleware(app: FastAPI):
    settings = Settings()

    app.add_middleware(PendingConsentMiddleware)

    app.add_middleware(LoggingMiddleware)  # novo
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=settings.cors_headers,
    )
