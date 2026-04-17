from src.etl.load_decfec import load_decfec
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import pymongo

from src.control import distribution_indices_procedures
from src.control import energy_losses_tariff_procedures
from src.control import network_structure_procedures
from src.etl.database import setup
from src.config.settings import Settings

# Initialize settings (loads .env)
settings = Settings()


def get_db() -> pymongo.MongoClient:
    """
    Get the MongoDB client instance.
    This function can be used with FastAPI Depends() for dependency injection,
    or called directly for backward compatibility.
    """
    # Return the app instance if available (typically in request context)
    # Otherwise, this will be set during lifespan startup
    if hasattr(get_db, '_client'):
        return get_db._client
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for app startup and shutdown.
    
    Startup:
    - Creates MongoDB connection with configured pool settings
    - Initializes database collections and indexes
    - Seeds synthetic data if needed
    
    Shutdown:
    - Closes MongoDB connection properly
    """
    
    # ======================
    # STARTUP
    # ======================
    
    # Create MongoDB client with connection pool configuration
    mongo_client = pymongo.MongoClient(
        settings.mongo_uri,
        maxPoolSize=settings.mongo_max_pool_size,
        serverSelectionTimeoutMS=settings.mongo_server_selection_timeout_ms,
        connectTimeoutMS=settings.mongo_connect_timeout_ms,
    )
    
    # Store client in app for access in routes
    app.mongodb = mongo_client
    # Also store in the get_db function for direct calls
    get_db._client = mongo_client
    
    # Initialize database collections and indexes
    setup()
    
    # Seed synthetic data if database is empty
    from src.model.seed import seed
    seed()
    
    yield
    
    # ======================
    # SHUTDOWN
    # ======================
    
    # Close MongoDB connection gracefully
    if hasattr(app, 'mongodb') and app.mongodb:
        app.mongodb.close()
        delattr(app, 'mongodb')
    
    # Clean up the get_db function reference
    if hasattr(get_db, '_client'):
        delattr(get_db, '_client')


app = FastAPI(lifespan=lifespan)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/process-decfec")
def process_decfec():
    try:
        result = load_decfec()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "message": "DECFEC processado com sucesso",
        **result,
    }


@app.get("/get-dec-fec")
async def get_dec_fec(
    request: Request,
    agent_acronym: str | None = None,
    cnpj_number: str | None = None,
    consumer_unit_set_id: str | None = None,
    indicator_type_code: str | None = None,
    year_min: int | None = None,
    period_min: int | None = None,
    year_max: int | None = None,
    period_max: int | None = None
):
    filterDict = {
        "agent_acronym": agent_acronym,
        "cnpj_number": cnpj_number,
        "consumer_unit_set_id": consumer_unit_set_id,
        "indicator_type_code": indicator_type_code,
        "period": {"$gte": period_min, "$lte": period_max},
        "year": {"$gte": year_min, "$lte": year_max}
    }
    
    procedure = distribution_indices_procedures.Distribution_indices_procedures(
        connection=request.app.mongodb
    )
    return procedure.getAll(filterDict)


@app.get("/get-energy-losses")
async def get_energy_losses(
    request: Request,
    distributor: str | None = None,
    distributor_slug: str | None = None,
    state: str | None = None,
    uf: str | None = None,
    process_date_min: str | None = None,
    process_date_max: str | None = None
):
    filterDict = {
        "distributor": distributor,
        "distributor_slug": distributor_slug,
        "state": state,
        "uf": uf,
        "process_date": {"$gte": process_date_min, "$lte": process_date_max}
    }
    
    procedure = energy_losses_tariff_procedures.Energy_losses_tariff_procedures(
        connection=request.app.mongodb
    )
    return procedure.getAll(filterDict)


@app.get("/network-structure/summary")
async def get_summary(request: Request):
    procedure = network_structure_procedures.NetworkStructureProcedures(
        connection=request.app.mongodb
    )
    return procedure.get_summary()


@app.get("/network-structure/assets")
async def get_assets(
    request: Request,
    region: str | None = None,
    type: str | None = None,
    status: str | None = None
):
    procedure = network_structure_procedures.NetworkStructureProcedures(
        connection=request.app.mongodb
    )
    return procedure.get_assets(region, type, status)


@app.get("/network-structure/transformer/{transformer_id}")
async def get_transformer_detail(request: Request, transformer_id: str):
    procedure = network_structure_procedures.NetworkStructureProcedures(
        connection=request.app.mongodb
    )
    return procedure.get_transformer_detail(transformer_id)


@app.get("/network-structure/substation/{substation_id}")
async def get_substation_detail(request: Request, substation_id: str):
    procedure = network_structure_procedures.NetworkStructureProcedures(
        connection=request.app.mongodb
    )
    return procedure.get_substation_detail(substation_id)