"""
pipeline/load_db.py

Loads processed data into normalised database tables:
- companies
- skills
- jobs
- job_skills
Creates indexes and runs a verification check.
"""

import logging
import os
import sys

# Ensure repository root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
import yaml
from sqlalchemy import func, select
from backend.app.db import Base, SessionLocal, engine
from backend.app.models.job import Company, Skill, Job, JobSkill

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("db_loader")

def load_data_to_db(
    skills_yaml_path: str = "data/skills.yaml",
    cleaned_jobs_path: str = "data/processed/jobs_cleaned.csv",
    job_skills_path: str = "data/processed/job_skills.csv"
):
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        # 1. Load canonical skills
        logger.info(f"Loading skills from '{skills_yaml_path}'...")
        with open(skills_yaml_path, "r", encoding="utf-8") as f:
            skills_data = yaml.safe_load(f).get("skills", [])
            
        skill_name_to_obj = {}
        # Fetch existing skills
        existing_skills = {s.name: s for s in session.scalars(select(Skill)).all()}
        
        new_skills = []
        for s_item in skills_data:
            name = s_item["canonical"]
            cat = s_item.get("category", "General")
            if name in existing_skills:
                skill_name_to_obj[name] = existing_skills[name]
            else:
                sk_obj = Skill(name=name, category=cat)
                session.add(sk_obj)
                new_skills.append(sk_obj)
                skill_name_to_obj[name] = sk_obj
                
        if new_skills:
            session.commit()
            for s in new_skills:
                session.refresh(s)
                skill_name_to_obj[s.name] = s
        logger.info(f"Total skills in database: {len(skill_name_to_obj)}")

        # 2. Load companies and jobs
        logger.info(f"Loading cleaned jobs from '{cleaned_jobs_path}'...")
        df_jobs = pd.read_csv(cleaned_jobs_path)
        
        # Load / cache companies
        existing_companies = {c.name: c for c in session.scalars(select(Company)).all()}
        unique_companies = df_jobs["company"].dropna().unique()
        
        new_companies = []
        for comp_name in unique_companies:
            if comp_name not in existing_companies:
                c_obj = Company(name=comp_name)
                session.add(c_obj)
                new_companies.append(c_obj)
                existing_companies[comp_name] = c_obj
                
        if new_companies:
            session.commit()
            for c in new_companies:
                session.refresh(c)
                existing_companies[c.name] = c
        logger.info(f"Total companies in database: {len(existing_companies)}")

        # Clear existing jobs if re-running
        existing_job_count = session.scalar(select(func.count(Job.id)))
        if existing_job_count > 0:
            logger.info(f"Clearing {existing_job_count} prior jobs for clean reload...")
            session.query(JobSkill).delete()
            session.query(Job).delete()
            session.commit()

        # Batch insert jobs
        logger.info(f"Inserting {len(df_jobs)} jobs...")
        job_records = []
        job_uid_to_id = {}
        
        for idx, row in df_jobs.iterrows():
            comp_id = existing_companies[row["company"]].id
            job_obj = Job(
                job_uid=row["job_id"],
                title=row["title"],
                role=row["role"],
                company_id=comp_id,
                location=row["location"],
                city=row["city"],
                min_exp=float(row["min_exp"]),
                max_exp=float(row["max_exp"]),
                salary_min_inr=int(row["salary_min_inr"]) if pd.notna(row["salary_min_inr"]) else None,
                salary_max_inr=int(row["salary_max_inr"]) if pd.notna(row["salary_max_inr"]) else None,
                salary_median_inr=int(row["salary_median_inr"]) if pd.notna(row["salary_median_inr"]) else None,
                description=row["description"],
                posted_date=str(row["posted_date"]) if pd.notna(row["posted_date"]) else None
            )
            session.add(job_obj)
            
        session.commit()
        
        # Map job_uid to generated db id
        for j in session.scalars(select(Job)).all():
            job_uid_to_id[j.job_uid] = j.id
            
        logger.info(f"Inserted {len(job_uid_to_id)} jobs into database.")

        # 3. Load job_skills associations
        logger.info(f"Loading job-skill associations from '{job_skills_path}'...")
        df_skills = pd.read_csv(job_skills_path)
        
        job_skill_links = []
        seen_pairs = set()
        
        for _, row in df_skills.iterrows():
            j_uid = row["job_id"]
            sk_name = row["skill_canonical"]
            
            db_job_id = job_uid_to_id.get(j_uid)
            db_skill = skill_name_to_obj.get(sk_name)
            
            if db_job_id and db_skill:
                pair = (db_job_id, db_skill.id)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    job_skill_links.append(JobSkill(job_id=db_job_id, skill_id=db_skill.id))
                    
        # Bulk insert job skills
        batch_size = 5000
        for i in range(0, len(job_skill_links), batch_size):
            session.bulk_save_objects(job_skill_links[i:i + batch_size])
            session.commit()
            
        logger.info(f"Inserted {len(job_skill_links)} job-skill associations.")
        
        # Verification query
        job_count = session.scalar(select(func.count(Job.id)))
        comp_count = session.scalar(select(func.count(Company.id)))
        skill_count = session.scalar(select(func.count(Skill.id)))
        js_count = session.scalar(select(func.count(JobSkill.job_id)))
        
        logger.info("=== Database Verification Summary ===")
        logger.info(f"Total Companies: {comp_count}")
        logger.info(f"Total Skills:    {skill_count}")
        logger.info(f"Total Jobs:      {job_count}")
        logger.info(f"Total Job-Skills:{js_count}")
        logger.info("=====================================")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error loading data into DB: {e}", exc_info=True)
        raise
    finally:
        session.close()

if __name__ == "__main__":
    load_data_to_db()
