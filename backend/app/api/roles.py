"""
backend/app/api/roles.py

Thin router for roles list and market metrics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db import get_db
from backend.app.schemas.role import RoleListResponse
from backend.app.services.role_service import get_roles_summary

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("", response_model=RoleListResponse)
def get_roles(db: Session = Depends(get_db)):
    return get_roles_summary(db)
