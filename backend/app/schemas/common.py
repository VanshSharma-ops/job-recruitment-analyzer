"""
backend/app/schemas/common.py

Shared schema models and helpers.
"""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    total: int = Field(description="Total matching records count")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, description="Number of items per page")
    total_pages: int = Field(ge=0, description="Total number of pages")
    items: List[T] = Field(description="List of records for the current page")
