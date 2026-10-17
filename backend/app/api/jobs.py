"""
backend/app/api/jobs.py

Thin router for job search and filtering.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.db import get_db
from backend.app.schemas.job import JobItem, JobListResponse
from backend.app.services.job_service import get_job_by_id, list_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("", response_model=JobListResponse)
def get_jobs(
    role: Optional[str] = Query(None, description="Filter by role taxonomy"),
    city: Optional[str] = Query(None, description="Filter by canonical city"),
    min_exp: Optional[float] = Query(None, ge=0, description="Minimum experience in years"),
    max_exp: Optional[float] = Query(None, ge=0, description="Maximum experience in years"),
    skills: Optional[List[str]] = Query(None, description="Filter by skills (repeatable query param)"),
    search: Optional[str] = Query(None, description="Search term for title or location"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    return list_jobs(
        db=db,
        role=role,
        city=city,
        min_exp=min_exp,
        max_exp=max_exp,
        skills=skills,
        search=search,
        page=page,
        page_size=page_size
    )

@router.get("/{job_id}", response_model=JobItem)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job posting with ID {job_id} not found.")
    return job
