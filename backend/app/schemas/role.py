"""
backend/app/schemas/role.py

Schemas for role taxonomies and overview metrics.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class RoleItem(BaseModel):
    role: str = Field(description="Canonical role name")
    posting_count: int = Field(description="Total number of postings for this role")
    percentage_of_all_jobs: float = Field(description="Percentage share of all job postings")
    median_salary_lpa: Optional[float] = Field(None, description="Median salary in LPA")
    sample_size: int = Field(description="Sample size of postings (n)")

class RoleListResponse(BaseModel):
    total_postings: int
    roles: List[RoleItem]
