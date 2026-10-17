# PROMPT.md — Build the Job Recruitment Analyzer

Read `AGENTS.md` first and follow it strictly, especially section 7 (design). Then build the project below in the phases listed. Stop after each phase, show me what works, and wait for my go-ahead.

## Project

**Job Recruitment Analyzer**: a web app that analyses job-market data to show demanded skills, salary trends, hiring locations, and skill gaps for different job roles. It is a data analysis product, not a job portal.

Flow: `Job data -> Data cleaning -> NLP/skill extraction -> PostgreSQL -> FastAPI -> React dashboard`

Stack: Python, Pandas, NLP (spaCy), PostgreSQL, FastAPI, React, Tailwind CSS.

## Features

1. Search and filter jobs by role, location, skills, and experience
2. Most demanded skills for a role, as a percentage of postings
3. Salary and experience trends
4. Top hiring companies and locations
5. Compare a user's skills with a role's requirements
6. Show the commonly required skills the user is missing, ranked by demand

## Example that must work

Role: Backend Developer

```
Top skills:   Python, SQL, Git, AWS, Docker, FastAPI
Your skills:  Python, SQL, Git
Missing:      AWS, Docker, FastAPI
```

The real output should include the percentage of postings that mention each skill, and the match percentage.

## Phases

### Phase 1: Data and pipeline
- Set up the repo layout from AGENTS.md, `docker-compose.yml` for Postgres, `.env.example`.
- Get data: use files in `data/raw/` if present, otherwise write `pipeline/seed.py` to generate a realistic dataset (at least 5,000 postings, 8 roles, 10 Indian cities, 100+ companies, salary correlated with experience and city, skills correlated with role).
- `clean.py`: dedupe, normalise city names, normalise role titles, parse salary to annual INR, handle missing values, log rows kept at each step.
- `skills.yaml` with 150+ skills and aliases. `extract_skills.py` uses spaCy PhraseMatcher with word-boundary-safe matching.
- `load_db.py` loads into normalised tables: `jobs`, `companies`, `skills`, `job_skills`, with indexes.
- Tests for cleaning and skill extraction (include tricky cases like `Go`, `R`, `C++`, `Node.js`).
- Done when: one command runs the whole pipeline and I can query the DB.

### Phase 2: API
- FastAPI app with the endpoints listed in AGENTS.md section 5, SQL aggregation, pagination, filters, typed schemas.
- `POST /api/gap` returns matched skills, missing skills ranked by demand, match percentage, and the sample size.
- pytest tests for services and one API test per router.
- Done when: tests pass and I can test everything from `/docs`.

### Phase 3: Frontend design plan
- Before any UI code, write the design plan required by AGENTS.md 7.3: palette, type, ASCII wireframes for the main screen and the skill-gap view, three principles. Review it against the banned list and show me what you changed.

### Phase 4: Frontend build
- React + Vite + TypeScript + Tailwind, following the design plan and AGENTS.md section 7.
- Screens: main analysis view (query sentence, top skills, salary, locations, companies), job search table, skill-gap view with the persistent "Your skills" panel.
- URL-synced filters, loading/empty/error states, responsive to 360px, keyboard accessible.
- Synthetic-data notice if the dataset is seeded.
- Done when: the full flow works against the real API, no mocked data in the frontend.

### Phase 5: Polish and review
- Critique the UI against AGENTS.md 7.1 and remove anything templated.
- Update the README with setup and run instructions.
- List what is not built or known to be weak.

## Definition of done

- Pipeline, API, and frontend run locally with documented commands
- Tests pass
- Every number in the UI comes from the database and shows its sample size
- Skill-gap feature works with real data
- The UI does not look like a generic AI-generated dashboard
