"""
backend/app/services/gap_service.py

Service for skill-gap comparison between user skills and role market demands.
Computes matched skills, missing skills ranked by demand, match percentage, and sample size.
"""

import os
from typing import List, Optional, Set
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from backend.app.models.job import Job, JobSkill, Skill
from backend.app.schemas.gap import (
    MatchedSkillItem, MissingSkillItem, SkillGapRequest, SkillGapResponse
)
from pipeline.extract_skills import SkillExtractor

# Lazy-loaded singleton for SkillExtractor to canonicalize user skills
_extractor: Optional[SkillExtractor] = None

def get_extractor() -> SkillExtractor:
    global _extractor
    if _extractor is None:
        yaml_path = os.path.join(os.path.dirname(__file__), "../../../data/skills.yaml")
        if not os.path.exists(yaml_path):
            yaml_path = "data/skills.yaml"
        _extractor = SkillExtractor(skills_yaml_path=yaml_path)
    return _extractor

def normalize_user_skills(raw_skills: List[str]) -> List[str]:
    """
    Takes raw skill strings/aliases from user (e.g. ['py', 'postgres', 'k8s'])
    and returns a sorted list of canonical skill names.
    """
    extractor = get_extractor()
    normalized: Set[str] = set()

    for item in raw_skills:
        if not item or not isinstance(item, str):
            continue
        cleaned = item.strip()
        # Direct check if already canonical
        if cleaned in extractor.canonical_skills:
            normalized.add(cleaned)
            continue
            
        # Try extraction via PhraseMatcher
        extracted = extractor.extract_skills(cleaned)
        if extracted:
            for s in extracted:
                normalized.add(s)
        else:
            # Fallback title-case check
            title_case = cleaned.title()
            if title_case in extractor.canonical_skills:
                normalized.add(title_case)
            else:
                # Keep original cleaned string if non-empty
                normalized.add(cleaned)

    return sorted(list(normalized))

def compute_skill_gap(db: Session, request: SkillGapRequest) -> SkillGapResponse:
    # 1. Normalize user skills
    user_canonicals = normalize_user_skills(request.skills)
    user_skill_set = set(user_canonicals)

    # 2. Build filters for role
    conditions = [Job.role.ilike(request.role.strip())]
    if request.city:
        conditions.append(Job.city.ilike(request.city.strip()))
    if request.min_exp is not None:
        conditions.append(Job.max_exp >= request.min_exp)
    if request.max_exp is not None:
        conditions.append(Job.min_exp <= request.max_exp)

    # 3. Calculate sample size (n)
    sample_size = db.scalar(select(func.count(Job.id)).where(*conditions)) or 0

    if sample_size == 0:
        return SkillGapResponse(
            role=request.role,
            sample_size=0,
            user_skills_normalized=user_canonicals,
            matched_skills=[],
            missing_skills=[],
            match_percentage=0.0,
            total_demanded_skills=0,
            summary_insight=f"No postings found for role '{request.role}' with the selected criteria."
        )

    # 4. Aggregated market demand for this role
    stmt = (
        select(
            Skill.name,
            Skill.category,
            func.count(JobSkill.job_id).label("mention_count")
        )
        .join(JobSkill, Skill.id == JobSkill.skill_id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(*conditions)
        .group_by(Skill.id, Skill.name, Skill.category)
        .order_by(desc("mention_count"))
    )

    all_demanded = db.execute(stmt).all()
    total_demanded_skills = len(all_demanded)

    # Focus on top 25 skills or skills with >= 10% demand
    matched_skills: List[MatchedSkillItem] = []
    missing_skills: List[MissingSkillItem] = []

    # For weighted match percentage calculation
    top_demands = all_demanded[:15]
    total_top_demand_weight = sum(cnt for _, _, cnt in top_demands) or 1
    matched_demand_weight = 0

    rank = 1
    for skill_name, category, count in all_demanded:
        pct = round((count / sample_size) * 100.0, 1)

        is_user_match = skill_name in user_skill_set

        if is_user_match:
            matched_skills.append(
                MatchedSkillItem(
                    skill=skill_name,
                    category=category,
                    mention_count=count,
                    demand_percentage=pct
                )
            )
            # Add to weighted score if in top demands
            if any(skill_name == td[0] for td in top_demands):
                matched_demand_weight += count
        else:
            missing_skills.append(
                MissingSkillItem(
                    skill=skill_name,
                    category=category,
                    mention_count=count,
                    demand_percentage=pct,
                    importance_rank=rank
                )
            )
            rank += 1

    # Match percentage weighted by market demand of top skills
    match_percentage = round((matched_demand_weight / total_top_demand_weight) * 100.0, 1)
    match_percentage = min(100.0, max(0.0, match_percentage))

    # 5. Formulate dynamic summary insight
    if missing_skills and missing_skills[0].demand_percentage >= 25.0:
        top_missing = missing_skills[0]
        insight = f"{top_missing.skill} appears in {top_missing.demand_percentage}% of {request.role} postings. You don't list it."
    elif not missing_skills:
        insight = f"You list all commonly demanded skills for {request.role} postings!"
    elif matched_skills:
        insight = f"You match {len(matched_skills)} key skills for {request.role}, but are missing {missing_skills[0].skill} ({missing_skills[0].demand_percentage}%)."
    else:
        top_wanted = all_demanded[0][0] if all_demanded else "core skills"
        insight = f"None of your skills match the top requirements for {request.role}. Consider learning {top_wanted}."

    return SkillGapResponse(
        role=request.role,
        sample_size=sample_size,
        user_skills_normalized=user_canonicals,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        match_percentage=match_percentage,
        total_demanded_skills=total_demanded_skills,
        summary_insight=insight
    )
