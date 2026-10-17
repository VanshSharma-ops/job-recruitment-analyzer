"""
backend/tests/test_api_routers.py

API router integration tests:
One test per router:
- GET /api/health
- GET /api/roles
- GET /api/jobs & GET /api/jobs/{id}
- GET /api/skills/top
- GET /api/salary
- GET /api/locations/top
- GET /api/companies/top
- POST /api/gap
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Job Recruitment Analyzer" in data["service"]

def test_api_roles_router(client):
    response = client.get("/api/roles")
    assert response.status_code == 200
    data = response.json()
    assert "roles" in data
    assert "total_postings" in data
    assert len(data["roles"]) >= 8
    
    first = data["roles"][0]
    assert "role" in first
    assert "posting_count" in first
    assert "sample_size" in first
    assert first["posting_count"] == first["sample_size"]

def test_api_jobs_router(client):
    # List endpoint with filters and pagination
    response = client.get("/api/jobs?role=Backend Developer&page=1&page_size=15")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert data["page"] == 1
    assert data["page_size"] == 15
    assert len(data["items"]) == 15
    
    # Detail endpoint
    job_id = data["items"][0]["id"]
    detail_res = client.get(f"/api/jobs/{job_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == job_id
    assert "skills" in detail
    assert "company" in detail

def test_api_jobs_not_found(client):
    res = client.get("/api/jobs/9999999")
    assert res.status_code == 404

def test_api_skills_top_router(client):
    response = client.get("/api/skills/top?role=Backend Developer&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "skills" in data
    assert "sample_size" in data
    assert data["sample_size"] > 0
    assert len(data["skills"]) <= 10
    
    top_skill = data["skills"][0]
    assert "skill" in top_skill
    assert "percentage" in top_skill
    assert "mention_count" in top_skill
    assert "sample_size" in top_skill

def test_api_salary_router(client):
    response = client.get("/api/salary?role=Backend Developer")
    assert response.status_code == 200
    data = response.json()
    assert "bands" in data
    assert "overall_sample_size" in data
    assert len(data["bands"]) == 5
    
    band = data["bands"][0]
    assert "exp_band" in band
    assert "sample_size" in band
    assert "median_lpa" in band

def test_api_locations_top_router(client):
    response = client.get("/api/locations/top?role=Backend Developer&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "locations" in data
    assert "total_postings" in data
    assert len(data["locations"]) <= 5
    
    loc = data["locations"][0]
    assert "city" in loc
    assert "posting_count" in loc
    assert "percentage" in loc

def test_api_companies_top_router(client):
    response = client.get("/api/companies/top?role=Backend Developer&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "companies" in data
    assert "total_postings" in data
    assert len(data["companies"]) <= 5
    
    comp = data["companies"][0]
    assert "company" in comp
    assert "posting_count" in comp
    assert "percentage" in comp

def test_api_gap_router(client):
    payload = {
        "role": "Backend Developer",
        "skills": ["python", "sql", "git"]
    }
    response = client.post("/api/gap", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["role"] == "Backend Developer"
    assert data["sample_size"] > 0
    assert "matched_skills" in data
    assert "missing_skills" in data
    assert "match_percentage" in data
    assert "summary_insight" in data
    
    # Check that missing skills have rank and demand percentage
    if len(data["missing_skills"]) > 0:
        first_missing = data["missing_skills"][0]
        assert first_missing["importance_rank"] == 1
        assert "demand_percentage" in first_missing

def test_api_gap_validation_error(client):
    # Empty role
    response = client.post("/api/gap", json={"role": "", "skills": ["python"]})
    assert response.status_code in (400, 422)
