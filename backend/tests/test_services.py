"""
backend/tests/test_services.py

Unit tests for backend analysis services:
- Skill normalization
- Gap calculation (sample size, matched, missing ranked by demand, match percentage)
- Salary aggregation by experience bands
- Top demanded skills aggregation
- Location & company aggregations
- Job listing with pagination & filters
"""

import os
import sys
import pytest

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.db import SessionLocal
from backend.app.schemas.gap import SkillGapRequest
from backend.app.services.company_service import get_top_companies
from backend.app.services.gap_service import compute_skill_gap, normalize_user_skills
from backend.app.services.job_service import get_job_by_id, list_jobs
from backend.app.services.location_service import get_top_locations
from backend.app.services.role_service import get_roles_summary
from backend.app.services.salary_service import get_salary_analysis
from backend.app.services.skill_service import get_top_skills

@pytest.fixture(scope="module")
def db_session():
    session = SessionLocal()
    yield session
    session.close()

# 1. Skill Normalization Test
def test_normalize_user_skills():
    raw_inputs = ["py", "nodejs", "k8s", "postgres", "aws", "reactjs", "c++", "go"]
    normalized = normalize_user_skills(raw_inputs)
    
    assert "Python" in normalized
    assert "Node.js" in normalized
    assert "Kubernetes" in normalized
    assert "PostgreSQL" in normalized
    assert "AWS" in normalized
    assert "React" in normalized
    assert "C++" in normalized
    assert "Go" in normalized

# 2. Skill Gap Calculation Test
def test_compute_skill_gap(db_session):
    request = SkillGapRequest(
        role="Backend Developer",
        skills=["Python", "SQL", "Git"]
    )
    res = compute_skill_gap(db=db_session, request=request)
    
    assert res.role == "Backend Developer"
    assert res.sample_size > 0
    assert len(res.user_skills_normalized) >= 3
    
    matched_names = [m.skill for m in res.matched_skills]
    assert "Python" in matched_names or "SQL" in matched_names or "Git" in matched_names
    
    # Missing skills should be ranked by demand
    assert len(res.missing_skills) > 0
    for idx, missing in enumerate(res.missing_skills, 1):
        assert missing.importance_rank == idx
        assert missing.demand_percentage >= 0
        assert missing.skill not in request.skills

    assert 0.0 <= res.match_percentage <= 100.0
    assert len(res.summary_insight) > 0
    assert "Backend Developer" in res.summary_insight

def test_compute_skill_gap_unknown_role(db_session):
    request = SkillGapRequest(
        role="Astronomer Specialist",
        skills=["Telescope", "Physics"]
    )
    res = compute_skill_gap(db=db_session, request=request)
    assert res.sample_size == 0
    assert res.match_percentage == 0.0
    assert len(res.matched_skills) == 0

# 3. Salary Aggregation Test
def test_get_salary_analysis(db_session):
    res = get_salary_analysis(db=db_session, role="Backend Developer")
    assert res.overall_sample_size > 0
    assert res.overall_median_lpa is not None
    assert len(res.bands) == 5
    
    # Check that freshers band (0-1 yrs) has reasonable median salary
    band_0_1 = next(b for b in res.bands if b.exp_band == "0-1 years")
    assert band_0_1.sample_size > 0
    assert band_0_1.median_lpa is not None
    assert band_0_1.median_lpa > 0

# 4. Top Demanded Skills Test
def test_get_top_skills(db_session):
    res = get_top_skills(db=db_session, role="Backend Developer", limit=10)
    assert res.sample_size > 0
    assert len(res.skills) <= 10
    assert len(res.skills) > 0
    
    # Check percentages are decreasing
    prev_pct = 100.0
    for s in res.skills:
        assert s.sample_size == res.sample_size
        assert s.percentage <= prev_pct
        prev_pct = s.percentage

# 5. Roles Summary Test
def test_get_roles_summary(db_session):
    res = get_roles_summary(db=db_session)
    assert res.total_postings > 0
    assert len(res.roles) >= 8
    
    roles_list = [r.role for r in res.roles]
    assert "Backend Developer" in roles_list
    assert "Frontend Developer" in roles_list
    assert "Data Engineer" in roles_list

# 6. Top Locations & Companies Test
def test_get_top_locations(db_session):
    res = get_top_locations(db=db_session, role="Backend Developer", limit=5)
    assert res.total_postings > 0
    assert len(res.locations) <= 5
    city_names = [l.city for l in res.locations]
    assert "Bengaluru" in city_names or "Delhi NCR" in city_names

def test_get_top_companies(db_session):
    res = get_top_companies(db=db_session, role="Backend Developer", limit=5)
    assert res.total_postings > 0
    assert len(res.companies) <= 5
    for c in res.companies:
        assert c.sample_size > 0
        assert c.percentage > 0

# 7. Job Listing & Filtering Test
def test_list_jobs(db_session):
    res = list_jobs(db=db_session, role="Backend Developer", page=1, page_size=10)
    assert res.total > 0
    assert res.page == 1
    assert len(res.items) == 10
    for item in res.items:
        assert item.role == "Backend Developer"
        assert item.company is not None
        assert len(item.skills) > 0

def test_get_job_by_id(db_session):
    first_job = list_jobs(db=db_session, page=1, page_size=1).items[0]
    fetched = get_job_by_id(db=db_session, job_id=first_job.id)
    assert fetched is not None
    assert fetched.id == first_job.id
    assert fetched.job_uid == first_job.job_uid
