"""
backend/tests/test_pipeline.py

Unit tests for:
1. Role normalisation
2. City normalisation
3. Experience string parsing
4. Salary parsing into annual INR
5. Tricky skill extraction (Go vs going/go, R vs letters, C++, Node.js)
6. Skill alias canonicalisation
"""

import os
import sys
import pytest

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from pipeline.clean import (
    normalise_city,
    normalise_role,
    parse_experience,
    parse_salary_inr
)
from pipeline.extract_skills import SkillExtractor

@pytest.fixture(scope="module")
def extractor():
    yaml_path = os.path.join(os.path.dirname(__file__), "../../data/skills.yaml")
    return SkillExtractor(skills_yaml_path=yaml_path)

# --- 1. Role Normalisation Tests ---
def test_normalise_role_canonical():
    assert normalise_role("Senior Backend Developer") == "Backend Developer"
    assert normalise_role("React.js Frontend Engineer") == "Frontend Developer"
    assert normalise_role("Fullstack Software Development Engineer") == "Full Stack Developer"
    assert normalise_role("Senior Big Data & ETL Engineer") == "Data Engineer"
    assert normalise_role("AI/ML Applied Scientist") == "Machine Learning Engineer"
    assert normalise_role("Lead Cloud & DevOps Engineer") == "DevOps Engineer"
    assert normalise_role("Senior BI & Product Data Analyst") == "Data Analyst"
    assert normalise_role("Cross-Platform Flutter Mobile Dev") == "Mobile Developer"

def test_normalise_role_unmapped():
    assert normalise_role("Human Resources Executive") is None
    assert normalise_role("") is None
    assert normalise_role(None) is None

# --- 2. City Normalisation Tests ---
def test_normalise_city_variations():
    assert normalise_city("Bangalore") == "Bengaluru"
    assert normalise_city("Bengaluru, Karnataka") == "Bengaluru"
    assert normalise_city("Gurgaon") == "Delhi NCR"
    assert normalise_city("Noida") == "Delhi NCR"
    assert normalise_city("New Delhi") == "Delhi NCR"
    assert normalise_city("Bombay") == "Mumbai"
    assert normalise_city("Navi Mumbai") == "Mumbai"
    assert normalise_city("Madras") == "Chennai"
    assert normalise_city("Calcutta") == "Kolkata"
    assert normalise_city("Secunderabad") == "Hyderabad"
    assert normalise_city("Cochin") == "Kochi"
    assert normalise_city("Ahmedabad") == "Ahmedabad"
    assert normalise_city("Jaipur") == "Jaipur"
    assert normalise_city("Pune City") == "Pune"

def test_normalise_city_unknown():
    assert normalise_city("London") is None
    assert normalise_city("") is None
    assert normalise_city(None) is None

# --- 3. Experience Parsing Tests ---
def test_parse_experience():
    assert parse_experience("0-1 years") == (0.0, 1.0)
    assert parse_experience("1 - 3 yrs") == (1.0, 3.0)
    assert parse_experience("Fresher") == (0.0, 1.0)
    assert parse_experience("5+ years") == (5.0, 8.0)
    assert parse_experience("3 to 6 years") == (3.0, 6.0)
    assert parse_experience("Senior Developer") == (5.0, 9.0)

# --- 4. Salary Parsing Tests ---
def test_parse_salary_lpa():
    # 8 - 12 LPA
    mn, mx, med = parse_salary_inr("8 - 12 LPA")
    assert mn == 800000
    assert mx == 1200000
    assert med == 1000000

    # 15 LPA single
    mn, mx, med = parse_salary_inr("15 LPA")
    assert mn == 1500000
    assert mx == 1500000
    assert med == 1500000

def test_parse_salary_inr_strings():
    # ₹800,000 - ₹1,200,000
    mn, mx, med = parse_salary_inr("₹800,000 - ₹1,200,000")
    assert mn == 800000
    assert mx == 1200000
    assert med == 1000000

def test_parse_salary_monthly():
    # ₹50,000 per month -> 600,000 annual
    mn, mx, med = parse_salary_inr("₹50,000 per month")
    assert mn == 600000
    assert mx == 600000
    assert med == 600000

def test_parse_salary_missing():
    assert parse_salary_inr("") == (None, None, None)
    assert parse_salary_inr(None) == (None, None, None)

# --- 5. Skill Extraction Tricky Cases ---
def test_skill_extraction_go(extractor):
    # Matches Go
    matched = extractor.extract_skills("The candidate will build microservices using Go and PostgreSQL.")
    assert "Go" in matched

    matched_alias = extractor.extract_skills("We need a backend developer with Golang and Redis expertise.")
    assert "Go" in matched_alias

    # Does NOT match ordinary English verbs "going" or "go"
    not_matched_going = extractor.extract_skills("We are going to deploy the product tomorrow.")
    assert "Go" not in not_matched_going

    not_matched_verb_go = extractor.extract_skills("Must go to the office twice a week.")
    assert "Go" not in not_matched_verb_go

def test_skill_extraction_r(extractor):
    # Matches R programming / R language
    matched_r_prog = extractor.extract_skills("Proficiency with R programming and statistical modeling.")
    assert "R" in matched_r_prog

    matched_r_lang = extractor.extract_skills("Experience with R language and Python.")
    assert "R" in matched_r_lang
    assert "Python" in matched_r_lang

    matched_exact_r = extractor.extract_skills("We use R and Python for analytics.")
    assert "R" in matched_exact_r

    # Does NOT match random text with letter 'r' or 'are'
    not_matched = extractor.extract_skills("We are looking for developers who work hard.")
    assert "R" not in not_matched

def test_skill_extraction_cpp(extractor):
    matched = extractor.extract_skills("Requires knowledge of C++ and STL algorithms.")
    assert "C++" in matched

    matched_alias = extractor.extract_skills("Must write modern cpp code.")
    assert "C++" in matched_alias

def test_skill_extraction_node(extractor):
    # Canonical Node.js and its aliases
    assert "Node.js" in extractor.extract_skills("Experience with Node.js and Express.")
    assert "Node.js" in extractor.extract_skills("Proficiency in nodejs and mongodb.")
    assert "Node.js" in extractor.extract_skills("Strong node js backend skills.")

def test_skill_extraction_aliases_canonicalisation(extractor):
    # AWS aliases
    assert "AWS" in extractor.extract_skills("Deployed on Amazon Web Services.")
    assert "AWS" in extractor.extract_skills("Experience with aws infrastructure.")

    # Kubernetes alias
    assert "Kubernetes" in extractor.extract_skills("Container orchestration with k8s.")

    # FastAPI alias
    assert "FastAPI" in extractor.extract_skills("REST APIs built with fast-api.")

    # PostgreSQL alias
    assert "PostgreSQL" in extractor.extract_skills("Database management using postgres and psql.")
