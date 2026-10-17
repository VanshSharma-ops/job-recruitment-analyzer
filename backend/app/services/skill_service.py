"""
backend/app/services/skill_service.py

Service for retrieving top demanded skills for a given role and optional filters.
Performs SQL aggregation with GROUP BY on indexed columns.
"""

from typing import Optional
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from backend.app.models.job import Job, JobSkill, Skill
from backend.app.schemas.skill import SkillDemanded, SkillTopResponse

def get_top_skills(
    db: Session,
    role: Optional[str] = None,
    city: Optional[str] = None,
    min_exp: Optional[float] = None,
    max_exp: Optional[float] = None,
    limit: int = 25
) -> SkillTopResponse:
    # Build filter conditions for Jobs
    conditions = []
    if role:
        conditions.append(Job.role.ilike(role.strip()))
    if city:
        conditions.append(Job.city.ilike(city.strip()))
    if min_exp is not None:
        conditions.append(Job.max_exp >= min_exp)
    if max_exp is not None:
        conditions.append(Job.min_exp <= max_exp)

    # 1. Calculate sample size (number of postings matching filters)
    sample_size_query = select(func.count(Job.id))
    if conditions:
        sample_size_query = sample_size_query.where(*conditions)
    sample_size = db.scalar(sample_size_query) or 0

    if sample_size == 0:
        return SkillTopResponse(
            role=role,
            city=city,
            sample_size=0,
            skills=[]
        )

    # 2. Aggregation query: Group by Skill
    stmt = (
        select(
            Skill.name,
            Skill.category,
            func.count(JobSkill.job_id).label("mention_count")
        )
        .join(JobSkill, Skill.id == JobSkill.skill_id)
        .join(Job, Job.id == JobSkill.job_id)
    )
    if conditions:
        stmt = stmt.where(*conditions)

    stmt = (
        stmt.group_by(Skill.id, Skill.name, Skill.category)
        .order_by(desc("mention_count"))
        .limit(limit)
    )

    results = db.execute(stmt).all()

    skills_demanded = []
    for skill_name, category, count in results:
        pct = round((count / sample_size) * 100.0, 1)
        skills_demanded.append(
            SkillDemanded(
                skill=skill_name,
                category=category,
                mention_count=count,
                percentage=pct,
                sample_size=sample_size
            )
        )

    return SkillTopResponse(
        role=role,
        city=city,
        sample_size=sample_size,
        skills=skills_demanded
    )
