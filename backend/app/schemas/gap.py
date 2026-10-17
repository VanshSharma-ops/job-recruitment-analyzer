"""
backend/app/schemas/gap.py

Schemas for Skill Gap Analysis:
Matches user skills with role requirements, ranking missing skills by market demand.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class SkillGapRequest(BaseModel):
    role: str = Field(description="Target role, e.g. 'Backend Developer'")
    skills: List[str] = Field(description="List of user's current skills or aliases, e.g. ['python', 'sql', 'git']")
    city: Optional[str] = Field(None, description="Optional city filter to narrow market demand")
    min_exp: Optional[float] = Field(None, description="Optional min experience filter")
    max_exp: Optional[float] = Field(None, description="Optional max experience filter")

class MatchedSkillItem(BaseModel):
    skill: str = Field(description="Canonical skill name")
    category: str = Field(description="Skill category")
    mention_count: int = Field(description="Number of role postings requiring this skill")
    demand_percentage: float = Field(description="Percentage of role postings requiring this skill")

class MissingSkillItem(BaseModel):
    skill: str = Field(description="Canonical skill name")
    category: str = Field(description="Skill category")
    mention_count: int = Field(description="Number of role postings requiring this skill")
    demand_percentage: float = Field(description="Percentage of role postings requiring this skill")
    importance_rank: int = Field(description="Rank ordered by market demand (1 = highest demand)")

class SkillGapResponse(BaseModel):
    role: str = Field(description="Analyzed role")
    sample_size: int = Field(description="Total role postings analyzed (n)")
    user_skills_normalized: List[str] = Field(description="Canonicalised user skills")
    matched_skills: List[MatchedSkillItem] = Field(description="Skills user has that match role demand")
    missing_skills: List[MissingSkillItem] = Field(description="Skills user lacks, ranked by demand")
    match_percentage: float = Field(description="Percentage match with top market demands")
    total_demanded_skills: int = Field(description="Total distinct skills demanded for this role")
    summary_insight: str = Field(description="Computed dynamic insight string")
