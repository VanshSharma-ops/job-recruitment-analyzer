"""
backend/app/schemas/location.py

Schemas for location and hiring cities analysis.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class LocationItem(BaseModel):
    city: str = Field(description="Canonical city name")
    posting_count: int = Field(description="Postings count in this location")
    percentage: float = Field(description="Percentage of total matching postings")
    median_salary_lpa: Optional[float] = Field(None, description="Median salary in LPA in this city")
    sample_size: int = Field(description="Postings sample size (n)")

class LocationTopResponse(BaseModel):
    role: Optional[str] = Field(None, description="Role filter applied")
    total_postings: int = Field(description="Total postings matching filters")
    locations: List[LocationItem]
