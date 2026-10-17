"""
backend/app/services/location_service.py

Service for top hiring cities analysis for a role.
Calculates posting counts, market share percentage, and median salary.
"""

from typing import Optional
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from backend.app.models.job import Job
from backend.app.schemas.location import LocationItem, LocationTopResponse

def get_top_locations(
    db: Session,
    role: Optional[str] = None,
    min_exp: Optional[float] = None,
    max_exp: Optional[float] = None,
    limit: int = 10
) -> LocationTopResponse:
    conditions = []
    if role:
        conditions.append(Job.role.ilike(role.strip()))
    if min_exp is not None:
        conditions.append(Job.max_exp >= min_exp)
    if max_exp is not None:
        conditions.append(Job.min_exp <= max_exp)

    # Total postings in subset
    total_query = select(func.count(Job.id))
    if conditions:
        total_query = total_query.where(*conditions)
    total_postings = db.scalar(total_query) or 0

    if total_postings == 0:
        return LocationTopResponse(
            role=role,
            total_postings=0,
            locations=[]
        )

    stmt = select(
        Job.city,
        func.count(Job.id).label("cnt"),
        func.avg(Job.salary_median_inr).label("avg_sal")
    )
    if conditions:
        stmt = stmt.where(*conditions)

    stmt = (
        stmt.group_by(Job.city)
        .order_by(desc("cnt"))
        .limit(limit)
    )

    results = db.execute(stmt).all()

    locations = []
    for city_name, cnt, avg_sal in results:
        pct = round((cnt / total_postings * 100.0), 1)
        med_lpa = round(avg_sal / 100000.0, 1) if avg_sal else None
        locations.append(
            LocationItem(
                city=city_name,
                posting_count=cnt,
                percentage=pct,
                median_salary_lpa=med_lpa,
                sample_size=cnt
            )
        )

    return LocationTopResponse(
        role=role,
        total_postings=total_postings,
        locations=locations
    )
