"""
backend/app/api/companies.py

Thin router for top hiring companies analysis.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db import get_db
from backend.app.schemas.company import CompanyTopResponse
from backend.app.services.company_service import get_top_companies

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("/top", response_model=CompanyTopResponse)
def get_top_hiring_companies(
    role: Optional[str] = Query(None, description="Role filter (e.g. 'Backend Developer')"),
    city: Optional[str] = Query(None, description="City filter"),
    min_exp: Optional[float] = Query(None, ge=0, description="Minimum experience filter"),
    max_exp: Optional[float] = Query(None, ge=0, description="Maximum experience filter"),
    limit: int = Query(15, ge=1, le=50, description="Number of companies to return"),
    db: Session = Depends(get_db)
):
    return get_top_companies(
        db=db,
        role=role,
        city=city,
        min_exp=min_exp,
        max_exp=max_exp,
        limit=limit
    )
