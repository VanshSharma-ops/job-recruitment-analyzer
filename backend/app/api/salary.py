"""
backend/app/api/salary.py

Thin router for salary distribution analysis by experience band.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db import get_db
from backend.app.schemas.salary import SalaryResponse
from backend.app.services.salary_service import get_salary_analysis

router = APIRouter(prefix="/salary", tags=["salary"])

@router.get("", response_model=SalaryResponse)
def get_salary(
    role: Optional[str] = Query(None, description="Role filter (e.g. 'Backend Developer')"),
    city: Optional[str] = Query(None, description="City filter (e.g. 'Bengaluru')"),
    db: Session = Depends(get_db)
):
    return get_salary_analysis(db=db, role=role, city=city)
