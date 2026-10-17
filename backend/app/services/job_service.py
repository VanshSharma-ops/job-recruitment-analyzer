"""
backend/app/services/job_service.py

Service for querying, filtering, and paginating job postings.
Uses real SQL queries and JOINs on indexed columns.
"""

from typing import List, Optional
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session, selectinload
from backend.app.models.job import Company, Job, JobSkill, Skill
from backend.app.schemas.job import JobItem, JobListResponse

def list_jobs(
    db: Session,
    role: Optional[str] = None,
    city: Optional[str] = None,
    min_exp: Optional[float] = None,
    max_exp: Optional[float] = None,
    skills: Optional[List[str]] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
) -> JobListResponse:
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    
    # Base query for filtering
    conditions = []
    
    if role:
        conditions.append(Job.role.ilike(role.strip()))
    if city:
        conditions.append(Job.city.ilike(city.strip()))
    if min_exp is not None:
        conditions.append(Job.max_exp >= min_exp)
    if max_exp is not None:
        conditions.append(Job.min_exp <= max_exp)
    if search:
        s = f"%{search.strip()}%"
        conditions.append(
            (Job.title.ilike(s)) | (Job.location.ilike(s))
        )
        
    query = select(Job).options(selectinload(Job.company), selectinload(Job.skills))
    count_query = select(func.count(distinct(Job.id)))
    
    if skills and len(skills) > 0:
        cleaned_skills = [s.strip() for s in skills if s.strip()]
        if cleaned_skills:
            # Join JobSkill and Skill for filtering
            query = query.join(Job.skills).where(Skill.name.in_(cleaned_skills))
            count_query = count_query.join(Job.skills).where(Skill.name.in_(cleaned_skills))
            
    if conditions:
        query = query.where(*conditions)
        count_query = count_query.where(*conditions)
        
    # Total count
    total = db.scalar(count_query) or 0
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    # Order by posted date desc and id desc
    offset = (page - 1) * page_size
    query = query.order_by(Job.posted_date.desc().nullslast(), Job.id.desc()).offset(offset).limit(page_size)
    
    jobs = db.scalars(query).unique().all()
    
    items = []
    for j in jobs:
        min_lpa = round(j.salary_min_inr / 100000.0, 1) if j.salary_min_inr else None
        max_lpa = round(j.salary_max_inr / 100000.0, 1) if j.salary_max_inr else None
        med_lpa = round(j.salary_median_inr / 100000.0, 1) if j.salary_median_inr else None
        
        items.append(JobItem(
            id=j.id,
            job_uid=j.job_uid,
            title=j.title,
            role=j.role,
            company=j.company.name if j.company else "Unknown",
            location=j.location,
            city=j.city,
            min_exp=j.min_exp,
            max_exp=j.max_exp,
            salary_min_inr=j.salary_min_inr,
            salary_max_inr=j.salary_max_inr,
            salary_median_inr=j.salary_median_inr,
            salary_min_lpa=min_lpa,
            salary_max_lpa=max_lpa,
            salary_median_lpa=med_lpa,
            description=j.description,
            posted_date=j.posted_date,
            skills=[s.name for s in j.skills]
        ))
        
    return JobListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items
    )

def get_job_by_id(db: Session, job_id: int) -> Optional[JobItem]:
    query = select(Job).options(selectinload(Job.company), selectinload(Job.skills)).where(Job.id == job_id)
    j = db.scalar(query)
    if not j:
        return None
        
    min_lpa = round(j.salary_min_inr / 100000.0, 1) if j.salary_min_inr else None
    max_lpa = round(j.salary_max_inr / 100000.0, 1) if j.salary_max_inr else None
    med_lpa = round(j.salary_median_inr / 100000.0, 1) if j.salary_median_inr else None
    
    return JobItem(
        id=j.id,
        job_uid=j.job_uid,
        title=j.title,
        role=j.role,
        company=j.company.name if j.company else "Unknown",
        location=j.location,
        city=j.city,
        min_exp=j.min_exp,
        max_exp=j.max_exp,
        salary_min_inr=j.salary_min_inr,
        salary_max_inr=j.salary_max_inr,
        salary_median_inr=j.salary_median_inr,
        salary_min_lpa=min_lpa,
        salary_max_lpa=max_lpa,
        salary_median_lpa=med_lpa,
        description=j.description,
        posted_date=j.posted_date,
        skills=[s.name for s in j.skills]
    )
