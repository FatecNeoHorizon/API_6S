from typing import List, Dict, Any, Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Depends
from src.api.dependencies.auth import AuthenticatedUser, get_current_user
from pymongo.database import Database
from bson.objectid import ObjectId

from src.database.connection import get_db

router = APIRouter()


@router.get("/conj")
def get_conj(
    year: Optional[int] = Query(default=None, ge=1900, le=2100),
    indicator_type_code: Optional[Literal["DEC", "FEC"]] = Query(default=None),
    db: Database = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Return CONJ documents as a GeoJSON FeatureCollection.

    Projects only `code`, `name` and `geometry`. Filters out documents
    without a filled `geometry` field and skips invalid geometries.
    """
    try:
        filters: Dict[str, Any] = {"geometry": {"$exists": True, "$ne": None}}
        elem_match: Dict[str, Any] = {}
        if year is not None:
            elem_match["year"] = year
        if indicator_type_code is not None:
            elem_match["indicator_type_code"] = indicator_type_code
        if elem_match:
            filters["annual_summaries"] = {"$elemMatch": elem_match}

        cursor = db["conj"].find(
            filters,
            {"code": 1, "name": 1, "geometry": 1, "annual_summaries": 1, "_id": 0},
        )

        features: List[Dict[str, Any]] = []
        for doc in cursor:
            geometry = doc.get("geometry")
            # Basic validation: must be a dict with type and coordinates
            if not isinstance(geometry, dict) or "type" not in geometry or "coordinates" not in geometry:
                continue

            annual_summaries = doc.get("annual_summaries") or []
            valid_summaries = [s for s in annual_summaries if isinstance(s, dict)]

            if year is not None or indicator_type_code is not None:
                summary = next(
                    (
                        s
                        for s in valid_summaries
                        if (year is None or s.get("year") == year)
                        and (
                            indicator_type_code is None
                            or s.get("indicator_type_code") == indicator_type_code
                        )
                    ),
                    None,
                )
                if summary is None:
                    continue
            else:
                summary = valid_summaries[0] if valid_summaries else {}

            properties = {
                "code": doc.get("code"),
                "name": doc.get("name"),
                "indicator_type_code": summary.get("indicator_type_code") if summary else None,
                "year": summary.get("year") if summary else None,
                "limit": summary.get("limit") if summary else None,
                "accumulated_value": summary.get("accumulated_value") if summary else None,
                "periods_count": summary.get("periods_count") if summary else None,
            }
            features.append({"type": "Feature", "properties": properties, "geometry": geometry})

        return {"type": "FeatureCollection", "features": features}

    except Exception:
        raise HTTPException(status_code=500, detail="Error reading CONJ collection")
    
@router.put("/update-conj")
def update_conj(
    id: Optional[str] = Query(default=None),
    update_index: Optional[int] = Query(default=None),
    new_value: Optional[float] = Query(default=None),
    new_name: Optional[str] = Query(default=None),
    db: Database = Depends(get_db),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    try:
        filter = {'_id': ObjectId(id)}

        annual_str = f"annual_summaries.{update_index}.accumulated_value"

        cursor = db["conj"].find_one_and_update(
            filter,
            {
                "$set": {
                "name": new_name,
                annual_str: new_value
                }
            }
        )
    except Exception:
         raise HTTPException(status_code=500, detail="Error updating CONJ collection")
