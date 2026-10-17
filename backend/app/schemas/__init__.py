from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.company import CompanyItem, CompanyTopResponse
from backend.app.schemas.gap import MatchedSkillItem, MissingSkillItem, SkillGapRequest, SkillGapResponse
from backend.app.schemas.job import JobItem, JobListResponse
from backend.app.schemas.location import LocationItem, LocationTopResponse
from backend.app.schemas.role import RoleItem, RoleListResponse
from backend.app.schemas.salary import SalaryByExperienceBand, SalaryResponse
from backend.app.schemas.skill import SkillDemanded, SkillTopResponse

__all__ = [
    "PaginatedResponse",
    "JobItem",
    "JobListResponse",
    "RoleItem",
    "RoleListResponse",
    "SkillDemanded",
    "SkillTopResponse",
    "SalaryByExperienceBand",
    "SalaryResponse",
    "LocationItem",
    "LocationTopResponse",
    "CompanyItem",
    "CompanyTopResponse",
    "SkillGapRequest",
    "SkillGapResponse",
    "MatchedSkillItem",
    "MissingSkillItem",
]
