"""
backend/app/api/gap.py

Thin router for Skill Gap Analysis.
POST /api/gap
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db import get_db
from backend.app.schemas.gap import SkillGapRequest, SkillGapResponse
from backend.app.services.gap_service import compute_skill_gap

router = APIRouter(prefix="/gap", tags=["gap"])

@router.post("", response_model=SkillGapResponse)
def analyze_skill_gap(request: SkillGapRequest, db: Session = Depends(get_db)):
    if not request.role or not request.role.strip():
        raise HTTPException(status_code=400, detail="The 'role' field is required.")
        
    return compute_skill_gap(db=db, request=request)
