"""
backend/app/main.py

FastAPI application entrypoint for Job Recruitment Analyzer.
Configures CORS, routes, error handlers, and OpenAPI documentation.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import companies, gap, jobs, locations, roles, salary, skills

load_dotenv()

app = FastAPI(
    title="Job Recruitment Analyzer API",
    description="Data analysis API for tech job postings, skills demand, salary trends, and skill gap comparison in India.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
cors_origins_env = os.getenv("CORS_ORIGIN", "http://localhost:5173")
origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]
if "*" not in origins and "http://localhost:5173" not in origins:
    origins.append("http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under /api
app.include_router(jobs.router, prefix="/api")
app.include_router(roles.router, prefix="/api")
app.include_router(skills.router, prefix="/api")
app.include_router(salary.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(gap.router, prefix="/api")

@app.get("/", include_in_schema=False)
def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

@app.get("/api/health", tags=["system"])
def health_check():
    return {
        "status": "ok",
        "service": "Job Recruitment Analyzer API",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=True)
