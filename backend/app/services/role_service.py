"""
backend/app/services/role_service.py

Service for retrieving roles and their aggregate market statistics.
Uses real SQL GROUP BY aggregation.
"""

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from backend.app.models.job import Job
from backend.app.schemas.role import RoleItem, RoleListResponse

def get_roles_summary(db: Session) -> RoleListResponse:
    total_postings = db.scalar(select(func.count(Job.id))) or 0
    
    # Aggregation per role
    stmt = (
        select(
            Job.role,
            func.count(Job.id).label("cnt"),
            func.avg(Job.salary_median_inr).label("avg_sal")
        )
        .group_by(Job.role)
        .order_by(desc("cnt"))
    )
    results = db.execute(stmt).all()
    
    items = []
    for role_name, cnt, avg_sal in results:
        pct = round((cnt / total_postings * 100.0), 1) if total_postings > 0 else 0.0
        med_lpa = round(avg_sal / 100000.0, 1) if avg_sal else None
        
        items.append(RoleItem(
            role=role_name,
            posting_count=cnt,
            percentage_of_all_jobs=pct,
            median_salary_lpa=med_lpa,
            sample_size=cnt
        ))
        
    return RoleListResponse(
        total_postings=total_postings,
        roles=items
    )
