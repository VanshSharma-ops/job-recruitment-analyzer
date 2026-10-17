"""
backend/app/services/salary_service.py

Service for calculating salary distributions by experience bands.
Exposes exact sample sizes (n), min, max, and median in LPA and annual INR.
"""

from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from backend.app.models.job import Job
from backend.app.schemas.salary import SalaryByExperienceBand, SalaryResponse

EXP_BANDS = [
    {"label": "0-1 years", "min_exp": 0.0, "max_exp": 1.0},
    {"label": "1-3 years", "min_exp": 1.0, "max_exp": 3.0},
    {"label": "3-6 years", "min_exp": 3.0, "max_exp": 6.0},
    {"label": "6-10 years", "min_exp": 6.0, "max_exp": 10.0},
    {"label": "10+ years", "min_exp": 10.0, "max_exp": 30.0},
]

def get_salary_analysis(
    db: Session,
    role: Optional[str] = None,
    city: Optional[str] = None
) -> SalaryResponse:
    base_conditions = [Job.salary_median_inr.isnot(None)]
    if role:
        base_conditions.append(Job.role.ilike(role.strip()))
    if city:
        base_conditions.append(Job.city.ilike(city.strip()))

    # Overall stats
    overall_stmt = select(
        func.count(Job.id).label("total_n"),
        func.avg(Job.salary_median_inr).label("overall_avg_sal")
    ).where(*base_conditions)
    overall_res = db.execute(overall_stmt).one()
    
    total_n = overall_res.total_n or 0
    overall_med_lpa = round(overall_res.overall_avg_sal / 100000.0, 1) if overall_res.overall_avg_sal else None

    band_results: List[SalaryByExperienceBand] = []

    for b in EXP_BANDS:
        # Condition matching experience overlap with the band
        band_conds = list(base_conditions)
        band_conds.append(Job.max_exp >= b["min_exp"])
        band_conds.append(Job.min_exp <= b["max_exp"])

        stmt = select(
            func.count(Job.id).label("band_n"),
            func.min(Job.salary_min_inr).label("min_sal"),
            func.max(Job.salary_max_inr).label("max_sal"),
            func.avg(Job.salary_median_inr).label("med_sal")
        ).where(*band_conds)

        row = db.execute(stmt).one()
        band_n = row.band_n or 0

        if band_n > 0:
            min_inr = int(row.min_sal) if row.min_sal else None
            max_inr = int(row.max_sal) if row.max_sal else None
            med_inr = int(row.med_sal) if row.med_sal else None
            min_lpa = round(min_inr / 100000.0, 1) if min_inr else None
            max_lpa = round(max_inr / 100000.0, 1) if max_inr else None
            med_lpa = round(med_inr / 100000.0, 1) if med_inr else None
        else:
            min_inr = max_inr = med_inr = min_lpa = max_lpa = med_lpa = None

        band_results.append(
            SalaryByExperienceBand(
                exp_band=b["label"],
                min_exp=b["min_exp"],
                max_exp=b["max_exp"],
                sample_size=band_n,
                median_lpa=med_lpa,
                min_lpa=min_lpa,
                max_lpa=max_lpa,
                median_inr=med_inr,
                min_inr=min_inr,
                max_inr=max_inr
            )
        )

    return SalaryResponse(
        role=role,
        city=city,
        overall_sample_size=total_n,
        overall_median_lpa=overall_med_lpa,
        bands=band_results
    )
