"""
backend/app/schemas/skill.py

Schemas for demanded skills and aggregations.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class SkillDemanded(BaseModel):
    skill: str = Field(description="Canonical skill name")
    category: str = Field(description="Skill category")
    mention_count: int = Field(description="Number of job postings requiring this skill")
    percentage: float = Field(description="Percentage of postings in role requiring this skill")
    sample_size: int = Field(description="Total role postings sample size (n)")

class SkillTopResponse(BaseModel):
    role: Optional[str] = Field(None, description="Queried role filter")
    city: Optional[str] = Field(None, description="Queried city filter")
    sample_size: int = Field(description="Total postings matching filters (n)")
    skills: List[SkillDemanded] = Field(description="Ranked demanded skills")
