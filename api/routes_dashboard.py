from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from utils.dependencies import get_db, ensure_default_user
from services.dashboard_service import get_dashboard_service

router = APIRouter()

@router.get("/")
def get_dashboard(db: Session = Depends(get_db)):
    ensure_default_user(db)
    return get_dashboard_service(db)
