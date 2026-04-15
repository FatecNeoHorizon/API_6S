from apps.backend.src.etl.load.load_decfec import load_decfec
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apps.backend.src.database.collections.database import setup

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup()
    from src.model.seed import seed
    seed()
    yield

app = FastAPI(lifespan=lifespan)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




