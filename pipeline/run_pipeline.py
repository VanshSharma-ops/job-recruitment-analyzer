"""
pipeline/run_pipeline.py

Executes the full pipeline in one command:
1. Seed raw data (if not already present or --force)
2. Clean data (deduping, normalisation, salary parsing, retention logging)
3. Extract skills (spaCy token PhraseMatcher with word boundaries)
4. Load database (normalised schema, companies, skills, jobs, job_skills)
5. Query verification
"""

import argparse
import logging
import os
import sys

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import desc, func, select
from backend.app.db import SessionLocal
from backend.app.models.job import Company, Job, JobSkill, Skill
from pipeline.clean import clean_data
from pipeline.extract_skills import run_extraction
from pipeline.load_db import load_data_to_db
from pipeline.seed import generate_dataset, save_dataset

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("pipeline_runner")

def verify_and_query_db():
    logger.info("Executing sample verification queries on the database...")
    session = SessionLocal()
    try:
        # 1. Total counts
        total_jobs = session.scalar(select(func.count(Job.id)))
        total_companies = session.scalar(select(func.count(Company.id)))
        total_skills = session.scalar(select(func.count(Skill.id)))
        
        logger.info(f"[DB Status] {total_jobs} jobs across {total_companies} companies and {total_skills} skills.")

        # 2. Sample query: Top 5 in-demand skills for 'Backend Developer'
        query_role = "Backend Developer"
        role_total = session.scalar(select(func.count(Job.id)).where(Job.role == query_role))
        
        logger.info(f"\n--- Sample Query: Demanded Skills for '{query_role}' (n = {role_total} postings) ---")
        top_skills = session.execute(
            select(
                Skill.name,
                func.count(JobSkill.job_id).label("mention_count")
            )
            .join(JobSkill, Skill.id == JobSkill.skill_id)
            .join(Job, Job.id == JobSkill.job_id)
            .where(Job.role == query_role)
            .group_by(Skill.id, Skill.name)
            .order_by(desc("mention_count"))
            .limit(8)
        ).all()

        for idx, (skill_name, count) in enumerate(top_skills, 1):
            pct = (count / role_total * 100) if role_total else 0
            logger.info(f"  {idx}. {skill_name:<20} {count:>4} postings ({pct:.1f}%)")

        # 3. Sample query: Salary by city for 'Backend Developer'
        logger.info(f"\n--- Sample Query: Median Annual Salary by City for '{query_role}' ---")
        salary_by_city = session.execute(
            select(
                Job.city,
                func.count(Job.id).label("postings"),
                func.avg(Job.salary_median_inr).label("avg_median_inr")
            )
            .where(Job.role == query_role, Job.salary_median_inr.isnot(None))
            .group_by(Job.city)
            .order_by(desc("avg_median_inr"))
            .limit(5)
        ).all()

        for city, count, avg_sal in salary_by_city:
            lpa = (avg_sal / 100000) if avg_sal else 0
            logger.info(f"  {city:<15} {lpa:>5.1f} LPA  (n = {count} postings)")

        logger.info("\nPipeline run and DB verification completed successfully!\n")
    finally:
        session.close()

def main():
    parser = argparse.ArgumentParser(description="Run complete data pipeline for Job Recruitment Analyzer")
    parser.add_argument("--force-seed", action="store_true", help="Force regenerate raw synthetic dataset")
    args = parser.parse_args()

    raw_csv = "data/raw/jobs_raw.csv"
    if args.force_seed or not os.path.exists(raw_csv):
        logger.info("[Step 1/4] Generating raw seed dataset...")
        postings = generate_dataset(5600)
        save_dataset(postings)
    else:
        logger.info(f"[Step 1/4] Using existing raw data at '{raw_csv}'")

    logger.info("[Step 2/4] Running data cleaning & normalisation...")
    clean_data()

    logger.info("[Step 3/4] Extracting skills using spaCy PhraseMatcher...")
    run_extraction()

    logger.info("[Step 4/4] Loading normalised tables into DB...")
    load_data_to_db()

    verify_and_query_db()

if __name__ == "__main__":
    main()
