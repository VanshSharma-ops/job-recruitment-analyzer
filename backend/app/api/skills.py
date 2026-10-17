"""
backend/app/api/skills.py

Thin router for top demanded skills by role.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db import get_db
from backend.app.schemas.skill import SkillTopResponse
from backend.app.services.skill_service import get_top_skills

router = APIRouter(prefix="/skills", tags=["skills"])

@router.get("/top", response_model=SkillTopResponse)
def get_top_demanded_skills(
    role: Optional[str] = Query(None, description="Target role name (e.g. 'Backend Developer')"),
    city: Optional[str] = Query(None, description="Optional city filter"),
    min_exp: Optional[float] = Query(None, ge=0, description="Minimum experience filter"),
    max_exp: Optional[float] = Query(None, ge=0, description="Maximum experience filter"),
    limit: int = Query(25, ge=1, le=100, description="Number of top skills to return"),
    db: Session = Depends(get_db)
):
    return get_top_skills(
        db=db,
        role=role,
        city=city,
        min_exp=min_exp,
        max_exp=max_exp,
        limit=limit
    )
