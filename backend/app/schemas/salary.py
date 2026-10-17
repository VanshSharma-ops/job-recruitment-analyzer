"""
backend/app/schemas/salary.py

Schemas for salary distributions across experience bands.
Exposes min, max, median in LPA and INR with exact sample size n.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class SalaryByExperienceBand(BaseModel):
    exp_band: str = Field(description="Experience band label, e.g. '0-1 years'")
    min_exp: float
    max_exp: float
    sample_size: int = Field(description="Number of postings disclosing salary in this band (n)")
    median_lpa: Optional[float] = Field(None, description="Median salary in LPA")
    min_lpa: Optional[float] = Field(None, description="25th percentile or min salary in LPA")
    max_lpa: Optional[float] = Field(None, description="75th percentile or max salary in LPA")
    median_inr: Optional[int] = Field(None, description="Median annual salary in INR")
    min_inr: Optional[int] = Field(None, description="Min annual salary in INR")
    max_inr: Optional[int] = Field(None, description="Max annual salary in INR")

class SalaryResponse(BaseModel):
    role: Optional[str] = Field(None, description="Queried role filter")
    city: Optional[str] = Field(None, description="Queried city filter")
    overall_sample_size: int = Field(description="Total postings with disclosed salary (n)")
    overall_median_lpa: Optional[float] = Field(None, description="Overall median salary in LPA")
    bands: List[SalaryByExperienceBand] = Field(description="Salary statistics per experience band")
