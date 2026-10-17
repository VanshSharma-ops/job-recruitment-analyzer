# DESIGN_PLAN.md — Job Recruitment Analyzer

## 1. Palette Specification

The app strictly adheres to the exact neutral and semantic palette defined in `AGENTS.md` section 7.2. No gradients, no rainbow accent colors, and no pure `#000000`.

```css
:root {
  --surface: #F2F4F3;      /* Crisp cool-neutral page background */
  --panel: #FFFFFF;        /* Data containers, tables, charts */
  --ink: #16201C;          /* Deep pine-black for primary text */
  --ink-soft: #5B6B64;     /* Muted slate-green for metadata & secondary labels */
  --matched: #1F6B54;      /* Forest green: skills user possesses & base bars */
  --missing: #B3261E;      /* Crimson red: skill deficit in target role */
  --rule: #D5DBD8;         /* Structural dividing lines, table rules */
  --rule-subtle: #E8ECEB;  /* Hairline row dividers */
}
```

Two semantic colours carry all functional meaning:
- `--matched` (`#1F6B54`): You have this skill / primary positive data.
- `--missing` (`#B3261E`): You lack this skill / gap alert.

---

## 2. Typography & Numbers

- **Font Family**: `Schibsted Grotesk`, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif.
- **Tabular Figures**: `font-variant-numeric: tabular-nums` applied globally to all numbers, percentages, salaries, and metrics to prevent jitter and maintain column alignment.
- **Text Transform**: Pure sentence case across the entire UI. No uppercase tracking or all-caps eyebrow labels.
- **Type Scale**:
  - `36px` / weight 700: Query sentence role and high-level headings.
  - `24px` / weight 700: Section titles and metric milestones.
  - `18px` / weight 500: Subheadings and table column groups.
  - `15px` / weight 400 & 500: Body text, table rows, filter select controls.
  - `13px` / weight 400: Metadata notes, sample size indicators (`n = 687`), footnote disclaimers.

---

## 3. Layout Wireframes (ASCII)

### 3.1 Main Analysis Screen (Desktop 1440px)
Asymmetric two-column split: Left 2/3 for interactive analysis; Right 1/3 for persistent "Your skills" workspace.

```text
+------------------------------------------------------------------------------------------------------------------+
| Job Recruitment Analyzer   [Persistent note: Synthetic seed dataset based on Indian tech market (5,600 postings)]|
+------------------------------------------------------------------------------------------------------------------+
|                                                                                                                  |
| QUERY SENTENCE CONTROL:                                                                                          |
| Show me [ Backend Developer v ] jobs in [ All India v ] with [ 0-2 years v ] experience.  [ Reset filters ]      |
|                                                                                                                  |
+-----------------------------------------------------------------------+------------------------------------------+
| MAIN ANALYSIS WORKBOOK (2/3 width)                                    | YOUR SKILLS (1/3 width, sticky)          |
+-----------------------------------------------------------------------+------------------------------------------+
| MARKET DEMAND FOR BACKEND DEVELOPER (n = 687 postings)                | YOUR PROFILE                             |
|                                                                       | 3 skills listed                          |
| Top demanded skills                     % of postings                 |                                          |
| -----------------------------------------------------------           | [ Enter a skill (e.g. Docker, Python) ]  |
| Node.js         [====================        ] 52.7% (missing)        | [ Add skill ]                            |
| Java            [==================          ] 49.2% (missing)        |                                          |
| Python          [==================          ] 48.9% (matched)        | CURRENT SKILLS:                          |
| Go              [=================           ] 46.7% (missing)        | * Python                   [x]           |
| Spring Boot     [================            ] 43.8% (missing)        | * SQL                      [x]           |
| Django          [================            ] 43.7% (missing)        | * Git                      [x]           |
| REST API        [================            ] 42.6% (missing)        |                                          |
| FastAPI         [================            ] 42.4% (missing)        | ---------------------------------------- |
| SQL             [===============             ] 40.9% (matched)        | QUICK GAP PREVIEW:                       |
| Git             [===============             ] 39.9% (matched)        | Match rate: 20.2%                        |
|                                                                       | Top missing:                             |
| --------------------------------------------------------------------- | 1. Node.js (52.7%)                       |
| SALARY BY EXPERIENCE BAND (n = 612 disclosing salary)                 | 2. Java (49.2%)                          |
|                                                                       | 3. Go (46.7%)                            |
| Band          Min        Median        Max          Sample size       |                                          |
| --------------------------------------------------------------------- | "Node.js appears in 52.7% of Backend     |
| 0-1 years     4.2 LPA ---[ 7.8 LPA ]--- 12.0 LPA    (n = 124)         |  Developer postings. You don't list it." |
| 1-3 years     6.5 LPA -----[ 12.4 LPA ]---- 18.5 LPA(n = 210)         |                                          |
| 3-6 years     11.0 LPA ------[ 20.2 LPA ]--- 32.0 LPA(n = 175)        | [ Compare my skills ] (Opens full gap)   |
| 6-10 years    18.0 LPA --------[ 34.5 LPA ]-- 52.0 LPA(n = 82)        |                                          |
| 10+ years     32.0 LPA -----------[ 56.0 LPA ] 85.0 LPA(n = 21)       +------------------------------------------+
|                                                                       |
| --------------------------------------------------------------------- |
| HIRING GEOGRAPHY                                TOP HIRING COMPANIES  |
| City            Share     Median LPA            Company      Postings |
| ------------------------------------            --------------------- |
| Bengaluru       34.8%     20.6 LPA              Flipkart           42 |
| Hyderabad       17.9%     18.7 LPA              Amazon India       38 |
| Delhi NCR       16.2%     19.7 LPA              Google India       31 |
| Pune            13.5%     19.0 LPA              Swiggy             29 |
| Mumbai           9.4%     19.5 LPA              CRED               24 |
+-----------------------------------------------------------------------+
```

### 3.2 Skill-Gap Dedicated View

```text
+------------------------------------------------------------------------------------------------------------------+
| <- Back to overview                                                                                              |
| SKILL GAP ANALYSIS: Backend Developer (n = 687 postings)                                                         |
| Match rating: 20.2% match against market demand                                                                  |
| "Node.js appears in 52.7% of Backend Developer postings. You don't list it."                                     |
+------------------------------------------------------------------------------------------------------------------+
|                                                                                                                  |
| WHAT YOU ARE MISSING (Ranked by employer demand)                                                                  |
| Rank  Skill          Category             In postings  Employer Demand Visual                      Action        |
| ---------------------------------------------------------------------------------------------------------------- |
|  1    Node.js        Backend Frameworks   362 (52.7%)  [====================          ]            [+ Add to mine]|
|  2    Java           Languages            338 (49.2%)  [==================            ]            [+ Add to mine]|
|  3    Go             Languages            321 (46.7%)  [=================             ]            [+ Add to mine]|
|  4    Spring Boot    Backend Frameworks   301 (43.8%)  [================              ]            [+ Add to mine]|
|  5    Django         Backend Frameworks   300 (43.7%)  [================              ]            [+ Add to mine]|
|  6    FastAPI        Backend Frameworks   291 (42.4%)  [================              ]            [+ Add to mine]|
|  7    Docker         Cloud & DevOps       282 (41.0%)  [===============               ]            [+ Add to mine]|
|                                                                                                                  |
| ---------------------------------------------------------------------------------------------------------------- |
| WHAT YOU ALREADY HAVE (3 skills matched)                                                                         |
| Skill        Category             In postings  Market Demand                                                     |
| ---------------------------------------------------------------------------------------------------------------- |
| Python       Languages            336 (48.9%)  [==================            ] (matched)                        |
| SQL          Languages            281 (40.9%)  [===============               ] (matched)                        |
| Git          Architecture         274 (39.9%)  [===============               ] (matched)                        |
+------------------------------------------------------------------------------------------------------------------+
```

---

## 4. Three Guiding Principles

1. **Analyst's Workbook, Not a Marketing Showcase**:
   - Zero marketing slogans ("Supercharge", "Unlock", "Seamless").
   - Dense, high-information-density tables and clear horizontal bars instead of generic puffy card grids.
   - Every number shows its exact sample size $n$. Any stat with $n < 20$ is subdued or flagged.

2. **Semantic Dual-Color System**:
   - Colors are strictly purposeful: Green (`--matched`) means the user has the qualification; Red (`--missing`) highlights the gap to bridge.
   - The UI canvas stays neutral and quiet so the user's attention is immediately drawn to where their career skill gaps lie.

3. **No Decorative Fluff or AI Stereotypes**:
   - No floating gradient blobs, no glassmorphism, no cards with soft shadows, no decorative emojis.
   - Clean 1px rules (`--rule`) and tabular layouts. At most two border radii: 0/2px for data tables and charts, 8px for buttons and interactive form controls.

---

## 5. Review Against Banned List (Section 7.1) & Explicit Changes Made

| Standard Dashboard Pattern (Banned) | What Was Changed & Implemented Instead |
|---|---|
| **Marketing Hero Section** (Big H1, subhead, "Get Started" button, 3 stat counters) | **Removed completely.** Replaced with a direct, functional sentence query: `Show me [Backend Developer] jobs in [All India] with [0-2 years] experience`. The tool is the first screen. |
| **Grid of identical rounded cards with drop shadows** | **Replaced with distinct structured data displays**: Horizontal ranked bars for skills, dot/range interval plots for salary bands, and dense compact tables for cities/companies. |
| **Purple/blue/pink gradients or glowing cards** | **Zero gradients.** Pure solid semantic tokens (`#1F6B54` matched, `#B3261E` missing, `#F2F4F3` background). |
| **Default Inter font with proportional numbers** | **Schibsted Grotesk with `tabular-nums`** so numbers and currency align in crisp columns without shifting. |
| **ALL-CAPS tracked-out eyebrows** (`FEATURE OVERVIEW`, `STATISTICS`) | **Pure sentence case everywhere.** Normal weight subheadings without forced capitalization. |
| **Generic emojis in labels** (e.g. `🚀 Skills`, `💰 Salary`, `📍 Cities`) | **Strictly zero emojis.** Data labels are textual, professional, and clear. |
| **One border radius on everything (e.g. `rounded-xl`)** | **Restricted to exactly two radii**: `0px` / `2px` for data tables and charts; `8px` for buttons and input fields. |
| **Area charts with smooth Bezier smoothing for salary** | **Discrete dot/range plots per experience band** showing min, median, and max with explicit sample sizes ($n$). |
