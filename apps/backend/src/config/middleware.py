from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config.pending_consent_middleware import PendingConsentMiddleware
from src.config.logging_middleware import LoggingMiddleware

def setup_middleware(app: FastAPI):

    app.add_middleware(PendingConsentMiddleware)

    app.add_middleware(LoggingMiddleware)  # novo
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )