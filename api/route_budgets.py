from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from schemas.budget import BudgetCreate, BudgetResponse
from models.budget import Budget
from utils.dependencies import get_db, ensure_default_user, current_user_id

router = APIRouter()

@router.post("/", response_model=BudgetResponse)
def create_budget(budget: BudgetCreate, db: Session = Depends(get_db)):
    ensure_default_user(db)
    db_budget = Budget(
        category=budget.category,
        amount=budget.amount,
        month=budget.month,
        user_id=current_user_id
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

@router.get("/", response_model=List[BudgetResponse])
def get_budgets(db: Session = Depends(get_db)):
    ensure_default_user(db)
    return db.query(Budget).filter(Budget.user_id == current_user_id).all()
