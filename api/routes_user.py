from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from utils.dependencies import get_db, ensure_default_user

router = APIRouter()

@router.post("/init")
def init_user(db: Session = Depends(get_db)):
    return ensure_default_user(db)
