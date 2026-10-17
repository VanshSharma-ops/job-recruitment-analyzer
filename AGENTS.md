# AGENTS.md — Job Recruitment Analyzer

Read this fully before writing any code. These rules override your defaults.

## 1. What this project is

A job-market analysis tool. It is NOT a job portal. Nobody applies to anything here.
The product answers: **"For this role, what skills does the market want, what does it pay, where is it hiring, and what am I missing?"**

Pipeline: `Job data -> cleaning (Pandas) -> skill extraction (NLP) -> PostgreSQL -> FastAPI -> React dashboard`

The primary user is an engineering student or fresher in India deciding what to learn next. Design and copy for that person.

## 2. Tech stack (fixed, do not swap)

- Backend: Python 3.11+, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2
- Data: Pandas, spaCy (PhraseMatcher / EntityRuler) plus a curated skills dictionary
- DB: PostgreSQL
- Frontend: React + Vite + TypeScript, Tailwind CSS, Recharts (or visx). No UI kit that imposes its own look (no shadcn defaults left untouched, no MUI, no Chakra)
- Tests: pytest for backend, Vitest for frontend utilities

## 3. Repo layout

```
job-analyzer/
  AGENTS.md
  README.md
  data/
    raw/            # untouched source files
    processed/      # cleaned output
    skills.yaml     # canonical skill list + aliases
  pipeline/
    clean.py
    extract_skills.py
    load_db.py
  backend/
    app/
      main.py
      api/          # routers: jobs, skills, salary, locations, companies, gap
      models/
      schemas/
      services/     # all analysis logic lives here, not in routers
      db.py
    alembic/
    tests/
  frontend/
    src/
      pages/
      components/
      lib/          # api client, formatters
      styles/
```

## 4. Data rules

- Use a real public dataset if one is provided in `data/raw/`. If none exists, generate a seed dataset with a script (`pipeline/seed.py`) with realistic distributions (skills correlated by role, salary correlated with experience and city). Never hand-write 10 fake rows.
- If data is seeded/synthetic, the UI must say so in a small persistent note. Never present fake data as real market data.
- Salary is stored as annual INR. Display as LPA (e.g. `8.5 LPA`). Show a range (min-max) or median with sample size, never a single made-up number.
- Every aggregate shown in the UI must expose its sample size (`n = 412 postings`). Hide or grey out stats with n < 20.
- Cleaning must handle: duplicate postings, missing salary, salary in different units, inconsistent city names (`Bangalore` / `Bengaluru`), inconsistent role titles (normalise to a role taxonomy).
- Skill extraction: normalise aliases to one canonical name (`node`, `nodejs`, `Node.js` -> `Node.js`). Match on word boundaries so `Go` does not match "going" and `R` does not match every letter. Keep the alias list in `skills.yaml`, not in code.
- Log how many rows survived each cleaning step.

## 5. Backend rules

- Routers are thin. Logic goes in `services/`.
- Every list endpoint supports filters (`role`, `city`, `min_exp`, `max_exp`, `skills`) and pagination.
- Required endpoints:
  - `GET /api/jobs` search and filter
  - `GET /api/roles` role list with posting counts
  - `GET /api/skills/top?role=` demanded skills with `% of postings`
  - `GET /api/salary?role=` salary by experience band
  - `GET /api/locations/top?role=` hiring cities
  - `GET /api/companies/top?role=` top hiring companies
  - `POST /api/gap` body `{ role, skills: [] }` returns matched, missing (ranked by demand), and a match percentage
- Use real SQL aggregation (GROUP BY, indexes on role/city/skill), not "load everything into Pandas per request".
- Typed request/response models everywhere. Proper HTTP errors with a useful message.
- CORS limited to the frontend origin from env. Secrets only from env. Provide `.env.example`.
- Provide `docker-compose.yml` for Postgres.
- Add pytest tests for: skill normalisation, gap calculation, salary aggregation, and one API test per router.

## 6. Frontend rules

- One typed API client in `lib/`. No fetch calls scattered in components.
- Every data view has loading, empty, and error states. Empty and error states say what happened and what to do next.
- Filters live in the URL query string so a view can be shared and the back button works.
- Responsive down to 360px. Visible keyboard focus. Respect `prefers-reduced-motion`. Contrast at least WCAG AA. Charts must be readable without relying on colour alone.
- No emoji in the UI.

## 7. Design: do not produce generic AI-looking output

This is the section most likely to be ignored. Do not ignore it.

### 7.1 Banned (these are the tells of generated sites)

- Purple/blue-to-pink gradients, gradient text, gradient blobs, glassmorphism, glow effects
- Cream background + serif + terracotta accent; or near-black background + one neon accent
- A hero with a big headline, a subhead, two buttons, and a row of three stats
- Content chopped into a grid of identical rounded cards with identical soft shadows
- One border-radius on everything
- A tracked-out ALL-CAPS eyebrow label above every heading
- Highlighting one word in a headline with a different colour/italic
- Numbered `01 / 02 / 03` markers on things that are not a sequence
- Fade-and-slide-up on every section, hover lift on every card
- Icons in coloured circles above feature text
- Lorem ipsum, "Acme Corp", "John Doe", or marketing copy like "Unlock the power of data", "Supercharge your career", "seamless", "leverage"
- A landing page. The first screen is the tool itself.
- Default Inter / Roboto / system-ui with default Tailwind grey/indigo

### 7.2 Direction to follow

**Concept:** an analyst's workbook, not a marketing site. Dense, legible, numbers-first, calm. Think a well-made statistics bulletin turned interactive, on a clean cool-neutral surface.

**First screen:** a single sentence-style query at the top that the user fills in: `Show me [Backend Developer] jobs in [All India] with [0-2 years] experience`. Each bracket is an inline control. Results appear directly below. No hero.

**Palette (use exactly these as CSS variables, adjust only for dark mode):**

| Token | Hex | Use |
|---|---|---|
| `--surface` | `#F2F4F3` | page background |
| `--panel` | `#FFFFFF` | table and chart areas |
| `--ink` | `#16201C` | text |
| `--ink-soft` | `#5B6B64` | secondary text |
| `--matched` | `#1F6B54` | skills the user has, primary bars |
| `--missing` | `#B3261E` | skills the user lacks |
| `--rule` | `#D5DBD8` | borders, gridlines |

Two colours carry meaning: green = you have it, red = you lack it. Do not add other accent colours. Do not use pure `#000`.

**Type:** one family, Schibsted Grotesk (fallback: system sans), weights 400/500/700. Use `font-variant-numeric: tabular-nums` on all numbers. Build a real type scale (e.g. 13 / 15 / 18 / 24 / 36). Body line length under 75 characters. Use sentence case everywhere. No all-caps labels.

**Layout:**
- Left-aligned. Asymmetric two-column layout on desktop: main analysis (about 2/3) and a persistent "Your skills" panel (about 1/3) that stays visible while browsing.
- Do not use a card grid. Use different structures for different data:
  - Top skills: ranked horizontal bars with the percentage at the end of each bar, matched skills in green, missing in red
  - Salary: a range/dot plot per experience band showing min, median, max, with `n` beside it (not a smooth area chart)
  - Hiring locations: a sorted table with an inline bar column
  - Companies: a plain ranked list with posting counts
  - Job search results: a dense table with sortable columns
- Use borders and rules for structure, not shadows. Use at most two border radii in the whole app (0 or 2px for data, 8px for inputs and buttons).
- Spend the design budget in one place: the skill-gap view is the memorable part. Keep everything else quiet.

**Motion:** none by default. Only motion that answers an action (a bar animating when the role changes, a panel opening). One short transition curve, reused everywhere.

**Copy:** plain and specific. Write for a student.
- Button: `Compare my skills`, `Add skill`, `Clear filters`. Not `Get started`, `Submit`, `Explore`
- Empty: `No postings match these filters. Try widening the experience range.`
- Error: `Couldn't load salary data. Check that the API is running, then retry.`
- Insight lines are computed from data, e.g. `Docker appears in 61% of Backend Developer postings. You don't list it.`

### 7.3 Before you build the UI

Write a short design plan (palette, type, layout wireframe in ASCII, three principles). Then check it against section 7.1. If any part looks like what you would produce for any dashboard, change it and say what you changed. Only then write code.

### 7.4 After you build the UI

Review it as a critic. Remove one decoration. Confirm that no banned pattern from 7.1 is present. If you can take screenshots, do it at 1440px and 390px and fix what looks templated.

## 8. Working style

- Build in the order given in PROMPT.md. Finish and verify each phase before starting the next.
- Ask before adding dependencies not listed in section 2.
- No placeholder functions that return hard-coded values. If something is not built, say so.
- Run tests and the app before claiming something works.
- Keep the README accurate: setup, env vars, how to run the pipeline, how to run backend and frontend.
- Commit-sized changes, clear names, no dead code, no commented-out blocks.
