
from fastapi import FastAPI, HTTPException
from src.control import energy_losses_tariff_procedures

@app.get("/get-energy-losses")
async def get_energy_losses(distributor: str | None = None, distributor_slug: str | None = None, state: str | None = None, 
                      uf : str | None = None, process_date_min: str | None = None, process_date_max: str | None = None):
    filterDict = {
        "distributor" : distributor,
        "distributor_slug" : distributor_slug,
        "state" : state,
        "uf" : uf,
        "process_date" : {"$gte" : process_date_min,
                "$lte" : process_date_max},
    }
    
    returnThing = energy_losses_tariff_procedures.Energy_losses_tariff_procedures().getAll(filterDict)
    return returnThing
