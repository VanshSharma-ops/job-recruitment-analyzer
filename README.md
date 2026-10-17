# Job Recruitment Analyzer

A data analysis product that analyses Indian tech job-market data to reveal demanded skills, compensation trends, hiring locations, and skill gaps for different roles.

> **Note**: This is an analyst's decision-support tool, not a job board or job application portal. It is designed for students and junior engineers in India deciding what technical skills to acquire next.

```text
Pipeline:
Job data -> Cleaning (Pandas) -> NLP Extraction (spaCy) -> PostgreSQL -> FastAPI -> React + Tailwind Dashboard
```

---

## Features

1. **Sentence Query Interface**: Direct interactive control replacing marketing heroes (`Show me [Backend Developer] jobs in [All India] with [0-2 years] experience`).
2. **Persistent Skills Workspace**: A sticky sidebar allowing users to maintain their technical skills profile across sessions (`localStorage`).
3. **Market Skills Demand**: Ranked horizontal bars showing `% of postings` demanding each skill, contrasting matched skills (green) against missing skills (red).
4. **Compensation by Experience Band**: Range/dot plots showing min, median, and max salaries in LPA across 5 experience tiers, highlighting exact sample sizes ($n$) and flagging $n < 20$.
5. **Geographical Hiring Distribution**: Sorted table with inline demand share bars and median salary across Indian tech hubs (Bengaluru, Hyderabad, Pune, Delhi NCR, Mumbai, etc.).
6. **Top Hiring Employers**: Ranked list of companies with highest hiring volume for the selected role.
7. **Skill Gap Analysis Engine (`POST /api/gap`)**: Normalises user skills, compares against employer requirements, ranks missing skills by market demand, and computes dynamic data-driven insights.
8. **Job Postings Explorer**: Dense, searchable, and sortable database table with pagination and expandable postings showing extracted skills tags.

---

## Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.x, Pydantic v2, Uvicorn
- **Data Pipeline**: Pandas, spaCy (`PhraseMatcher` with token-boundary safety), PyYAML
- **Database**: PostgreSQL 16 (with SQLite fallback for local development without Docker)
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Lucide icons (Zero UI kits, no generic AI styling)
- **Testing**: pytest (backend services & API routers), Vitest (frontend formatters)

---

## Directory Structure

```text
job-analyzer/
├── AGENTS.md                  # Core project constraints and design requirements
├── PROMPT.md                  # Development phases and verification rules
├── README.md                  # Setup and usage documentation
├── docker-compose.yml         # Containerized PostgreSQL service
├── .env.example               # Environment variables template
├── data/
│   ├── raw/                   # Untouched source files (jobs_raw.csv)
│   ├── processed/             # Cleaned output & extracted skill associations
│   └── skills.yaml            # 180+ canonical skills, categories & aliases
├── pipeline/
│   ├── seed.py                # Realistic dataset generator (5,800+ postings)
│   ├── clean.py               # Deduplication, normalisation & salary parser
│   ├── extract_skills.py      # spaCy PhraseMatcher with boundary safety
│   ├── load_db.py             # Normalised database loader with indexes
│   └── run_pipeline.py        # Single-command pipeline orchestrator
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI application & CORS configuration
│   │   ├── db.py              # SQLAlchemy 2.0 engine & session maker
│   │   ├── models/            # Company, Skill, Job, JobSkill models
│   │   ├── schemas/           # Pydantic request & response schemas
│   │   ├── services/          # Pure SQL aggregation & business logic
│   │   └── api/               # Thin routers (jobs, roles, skills, salary, gap, etc.)
│   └── tests/
│       ├── test_pipeline.py   # Cleaning, normalisation & tricky NLP token tests
│       ├── test_services.py   # Service aggregation & skill gap unit tests
│       └── test_api_routers.py# API router integration tests
├── frontend/
│   ├── src/
│   │   ├── components/        # Dense, numbers-first workbook components
│   │   ├── lib/               # Typed API client, schemas & formatters
│   │   ├── styles/            # CSS variables & typography tokens
│   │   ├── App.tsx            # URL-synced state container
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
└── docs/
    └── DESIGN_PLAN.md         # Wireframes, typography & banned-list audit
```

---

## Quick Start & Setup

### 1. Environment Configuration

Clone or navigate to the repository:
```bash
cd job-analyzer
cp .env.example .env
```

Default `.env` configuration:
```env
# Database connection:
DATABASE_URL=postgresql+psycopg2://postgres:postgrespassword@localhost:5432/job_analyzer
# SQLite fallback (enabled for local testing without Docker):
# DATABASE_URL=sqlite:///./data/job_analyzer.db

CORS_ORIGIN=http://localhost:5173
PORT=8000
ENVIRONMENT=development
```

### 2. Python Virtual Environment & Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pydantic sqlalchemy alembic psycopg2-binary pandas spacy pyyaml pytest python-dotenv httpx
```

### 3. Database Setup

To start PostgreSQL via Docker:
```bash
docker compose up -d
```
*(If Docker is not installed, you can set `DATABASE_URL=sqlite:///./data/job_analyzer.db` in `.env` to run with the SQLite engine).*

---

## Running the Data Pipeline

Run the entire pipeline (data generation, cleaning, skill extraction, database indexing, and verification queries) with a single command:

```bash
python pipeline/run_pipeline.py
```

To force regeneration of the synthetic raw dataset:
```bash
python pipeline/run_pipeline.py --force-seed
```

Individual pipeline scripts can also be executed independently:
- `python pipeline/seed.py`: Generates 5,800+ realistic job postings across 8 roles, 10 Indian cities, and 109 employers.
- `python pipeline/clean.py`: Deduplicates postings, normalises titles/cities, parses salaries to annual INR, and logs row counts.
- `python pipeline/extract_skills.py`: Extracts skills using spaCy `PhraseMatcher` on token boundaries.
- `python pipeline/load_db.py`: Creates normalised tables (`companies`, `skills`, `jobs`, `job_skills`) with indexes.

---

## Running the Backend API

Start the FastAPI server:
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

- API Base URL: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

### API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check endpoint |
| `GET` | `/api/roles` | Role taxonomy with posting counts and sample sizes |
| `GET` | `/api/jobs` | Search & filter postings by role, city, experience, skills with pagination |
| `GET` | `/api/jobs/{id}` | Detailed job posting record |
| `GET` | `/api/skills/top` | Top demanded skills for role/city with `% of postings` |
| `GET` | `/api/salary` | Salary ranges (min, median, max in LPA) across 5 experience bands |
| `GET` | `/api/locations/top` | Top hiring cities with posting counts and median salary |
| `GET` | `/api/companies/top` | Top hiring companies with posting counts |
| `POST` | `/api/gap` | Compare user skills with role demand, returning ranked missing skills and match score |

---

## Running the Frontend

Navigate to `frontend/`:
```bash
cd frontend
npm install
npm run dev
```

The frontend dashboard will be available at `http://localhost:5173`.

To build for production:
```bash
npm run build
```

---

## Running Tests

### Backend Test Suite (pytest)
```bash
pytest backend/tests/ -v
```
Runs 34 tests covering:
- Role normalisation and unmapped title handling
- City normalisation (`Bangalore` -> `Bengaluru`, `Gurgaon` -> `Delhi NCR`)
- Experience parsing (`0-1 yrs`, `Fresher`, `3-6 yrs`)
- Salary parsing from LPA ranges, monthly figures, and INR strings
- Tricky NLP token extraction (`Go` vs `going`/`go`, `R` vs arbitrary letters, `C++`, `Node.js`)
- Skill alias canonicalisation
- Services: Skill gap computation, salary aggregation, top skills/locations/companies
- API router endpoints: 200 responses, 404 handling, and validation errors

### Frontend Test Suite (Vitest)
```bash
cd frontend
npm test
```
Runs Vitest unit tests verifying number and currency formatting, sample size string representation, and experience range labeling.

---

## Skill Gap Calculation Example

Request:
```bash
curl -X POST "http://localhost:8000/api/gap" \
     -H "Content-Type: application/json" \
     -d '{"role": "Backend Developer", "skills": ["Python", "SQL", "Git"]}'
```

Response:
```json
{
  "role": "Backend Developer",
  "sample_size": 687,
  "user_skills_normalized": ["Git", "Python", "SQL"],
  "matched_skills": [
    { "skill": "Python", "category": "Programming Languages", "mention_count": 336, "demand_percentage": 48.9 },
    { "skill": "SQL",    "category": "Programming Languages", "mention_count": 281, "demand_percentage": 40.9 },
    { "skill": "Git",    "category": "Practices & Architecture", "mention_count": 274, "demand_percentage": 39.9 }
  ],
  "missing_skills": [
    { "skill": "Node.js",     "category": "Backend Frameworks", "mention_count": 362, "demand_percentage": 52.7, "importance_rank": 1 },
    { "skill": "Java",        "category": "Programming Languages", "mention_count": 338, "demand_percentage": 49.2, "importance_rank": 2 },
    { "skill": "Go",          "category": "Programming Languages", "mention_count": 321, "demand_percentage": 46.7, "importance_rank": 3 },
    { "skill": "Spring Boot", "category": "Backend Frameworks", "mention_count": 301, "demand_percentage": 43.8, "importance_rank": 4 },
    { "skill": "Django",      "category": "Backend Frameworks", "mention_count": 300, "demand_percentage": 43.7, "importance_rank": 5 },
    { "skill": "REST API",    "category": "Backend Frameworks", "mention_count": 293, "demand_percentage": 42.6, "importance_rank": 6 },
    { "skill": "FastAPI",     "category": "Backend Frameworks", "mention_count": 291, "demand_percentage": 42.4, "importance_rank": 7 },
    { "skill": "PostgreSQL",  "category": "Databases",          "mention_count": 286, "demand_percentage": 41.6, "importance_rank": 8 },
    { "skill": "Docker",      "category": "Cloud & DevOps",     "mention_count": 282, "demand_percentage": 41.0, "importance_rank": 9 }
  ],
  "match_percentage": 20.2,
  "total_demanded_skills": 26,
  "summary_insight": "Node.js appears in 52.7% of Backend Developer postings. You don't list it."
}
```

---

## Design System Compliance

This project strictly follows the anti-AI-cliché design guidelines in `AGENTS.md` Section 7:
- **No Marketing Hero**: The first screen is the functional sentence query tool itself.
- **Strict Color Semantics**: Only two accent colors carry meaning (`--matched` green for skills you have, `--missing` red for skills you lack). The page surface is a calm `#F2F4F3`.
- **Information Density**: Discrete horizontal ranked bars for skills, dot/range plots for salary, and dense tables for cities and employers. No generic card grids.
- **Tabular Numerics**: `Schibsted Grotesk` with `tabular-nums` applied globally for jitter-free data alignment.
- **Sample Size Transparency**: Every aggregate exposes its sample size (`n = ... postings`), with $n < 20$ flagged or greyed out.

---

## Known Limitations & Trade-offs

1. **Synthetic Seed Data**: While statistically correlated to reflect Indian hiring distributions (Bengaluru/NCR dominance, experience scaling, tech stacks), the current seed data is synthetically generated via `pipeline/seed.py`. The UI displays a persistent disclaimer in the top banner.
2. **Dictionary-Bound Extraction**: Skill extraction relies on `data/skills.yaml` (180+ skills) paired with spaCy `PhraseMatcher`. Brand new frameworks or niche abbreviations not listed in `skills.yaml` will not be matched unless added to the YAML taxonomy.
3. **Salary Formats**: The cleaner handles LPA expressions (`8 - 12 LPA`), standard INR figures (`₹12,00,000`), and monthly salaries (`₹60,000/mo`). Exotic compensation structures (e.g., hourly USD contracting rates or ESOP-heavy packages without base pay) are marked as undisclosed.
4. **Single-Node DB Optimization**: Indexes are placed on `(role, city)`, `(min_exp, max_exp)`, `company_id`, and `skill_id`. For production deployments exceeding millions of postings, read replicas or pre-aggregated materialized views would be beneficial for high concurrency.
