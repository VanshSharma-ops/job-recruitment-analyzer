"""
backend/app/schemas/job.py

Pydantic v2 schemas for job records, search, and filtering.
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from backend.app.schemas.common import PaginatedResponse

class JobItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_uid: str
    title: str
    role: str
    company: str
    location: str
    city: str
    min_exp: float
    max_exp: float
    salary_min_inr: Optional[int] = None
    salary_max_inr: Optional[int] = None
    salary_median_inr: Optional[int] = None
    salary_min_lpa: Optional[float] = None
    salary_max_lpa: Optional[float] = None
    salary_median_lpa: Optional[float] = None
    description: str
    posted_date: Optional[str] = None
    skills: List[str] = Field(default_factory=list)

class JobListResponse(PaginatedResponse[JobItem]):
    pass
