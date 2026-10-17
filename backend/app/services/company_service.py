"""
backend/app/services/company_service.py

Service for top hiring companies analysis.
Aggregates company posting volumes and salary metrics using SQL GROUP BY.
"""

from typing import Optional
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from backend.app.models.job import Company, Job
from backend.app.schemas.company import CompanyItem, CompanyTopResponse

def get_top_companies(
    db: Session,
    role: Optional[str] = None,
    city: Optional[str] = None,
    min_exp: Optional[float] = None,
    max_exp: Optional[float] = None,
    limit: int = 15
) -> CompanyTopResponse:
    conditions = []
    if role:
        conditions.append(Job.role.ilike(role.strip()))
    if city:
        conditions.append(Job.city.ilike(city.strip()))
    if min_exp is not None:
        conditions.append(Job.max_exp >= min_exp)
    if max_exp is not None:
        conditions.append(Job.min_exp <= max_exp)

    # Total matching postings
    total_query = select(func.count(Job.id))
    if conditions:
        total_query = total_query.where(*conditions)
    total_postings = db.scalar(total_query) or 0

    if total_postings == 0:
        return CompanyTopResponse(
            role=role,
            city=city,
            total_postings=0,
            companies=[]
        )

    stmt = (
        select(
            Company.name,
            func.count(Job.id).label("cnt"),
            func.avg(Job.salary_median_inr).label("avg_sal")
        )
        .join(Job, Job.company_id == Company.id)
    )
    if conditions:
        stmt = stmt.where(*conditions)

    stmt = (
        stmt.group_by(Company.id, Company.name)
        .order_by(desc("cnt"))
        .limit(limit)
    )

    results = db.execute(stmt).all()

    companies = []
    for comp_name, cnt, avg_sal in results:
        pct = round((cnt / total_postings * 100.0), 1)
        med_lpa = round(avg_sal / 100000.0, 1) if avg_sal else None
        companies.append(
            CompanyItem(
                company=comp_name,
                posting_count=cnt,
                percentage=pct,
                median_salary_lpa=med_lpa,
                sample_size=cnt
            )
        )

    return CompanyTopResponse(
        role=role,
        city=city,
        total_postings=total_postings,
        companies=companies
    )
