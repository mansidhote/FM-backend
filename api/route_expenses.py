from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from schemas.expense import ExpenseCreate, ExpenseResponse
from services.expense_crud import create_expense, get_user_expenses
from utils.dependencies import get_db, ensure_default_user

router = APIRouter()

@router.post("/", response_model=ExpenseResponse)
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    ensure_default_user(db)
    return create_expense(db, expense)

@router.get("/", response_model=List[ExpenseResponse])
def list_expenses(db: Session = Depends(get_db)):
    ensure_default_user(db)
    return get_user_expenses(db)
