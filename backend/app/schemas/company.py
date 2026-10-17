"""
backend/app/schemas/company.py

Schemas for top hiring employers and companies.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class CompanyItem(BaseModel):
    company: str = Field(description="Company name")
    posting_count: int = Field(description="Postings count from this company")
    percentage: float = Field(description="Percentage of total matching postings")
    median_salary_lpa: Optional[float] = Field(None, description="Median salary in LPA at this company")
    sample_size: int = Field(description="Sample size of company postings (n)")

class CompanyTopResponse(BaseModel):
    role: Optional[str] = Field(None, description="Role filter applied")
    city: Optional[str] = Field(None, description="City filter applied")
    total_postings: int = Field(description="Total postings matching filters")
    companies: List[CompanyItem]
