"""
backend/app/models/job.py

SQLAlchemy 2.0 ORM models for:
- Company
- Skill
- Job
- JobSkill (association table)
"""

from typing import List, Optional
from sqlalchemy import (
    Column, Integer, BigInteger, Float, String, Text, ForeignKey, Table,
    Index, DateTime, func
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from backend.app.db import Base

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, server_default=func.now())

    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="company")

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="General", index=True)

    jobs: Mapped[List["Job"]] = relationship(
        "Job",
        secondary="job_skills",
        back_populates="skills"
    )

class JobSkill(Base):
    __tablename__ = "job_skills"

    job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        primary_key=True,
        index=True
    )
    skill_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
        index=True
    )

    __table_args__ = (
        Index("ix_job_skills_skill_job", "skill_id", "job_id"),
    )

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_uid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    min_exp: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    max_exp: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    
    salary_min_inr: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    salary_max_inr: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    salary_median_inr: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, index=True)
    
    description: Mapped[str] = mapped_column(Text, nullable=False)
    posted_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)

    company: Mapped["Company"] = relationship("Company", back_populates="jobs")
    skills: Mapped[List["Skill"]] = relationship(
        "Skill",
        secondary="job_skills",
        back_populates="jobs"
    )

    __table_args__ = (
        Index("ix_jobs_role_city", "role", "city"),
        Index("ix_jobs_role_exp", "role", "min_exp", "max_exp"),
        Index("ix_jobs_city_exp", "city", "min_exp", "max_exp"),
    )
