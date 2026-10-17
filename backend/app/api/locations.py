"""
backend/app/api/locations.py

Thin router for top hiring locations analysis.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db import get_db
from backend.app.schemas.location import LocationTopResponse
from backend.app.services.location_service import get_top_locations

router = APIRouter(prefix="/locations", tags=["locations"])

@router.get("/top", response_model=LocationTopResponse)
def get_top_hiring_locations(
    role: Optional[str] = Query(None, description="Role filter (e.g. 'Backend Developer')"),
    min_exp: Optional[float] = Query(None, ge=0, description="Minimum experience filter"),
    max_exp: Optional[float] = Query(None, ge=0, description="Maximum experience filter"),
    limit: int = Query(10, ge=1, le=50, description="Number of locations to return"),
    db: Session = Depends(get_db)
):
    return get_top_locations(
        db=db,
        role=role,
        min_exp=min_exp,
        max_exp=max_exp,
        limit=limit
    )
