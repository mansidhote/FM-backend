from sqlalchemy.orm import Session
from models.expense import Expense
from schemas.expense import ExpenseCreate
from utils.dependencies import current_user_id
from app.ai import model

def create_expense(db: Session, expense: ExpenseCreate):
    category = expense.category
    if not category and model:
        try:
            prompt = f"Categorize this expense into one of these categories: Food, Transportation, Entertainment, Shopping, Bills, Other. Expense: '{expense.description} ${expense.amount}'. Respond with only the category name."
            response = model.generate_content(prompt)
            category = response.text.strip()
        except:
            category = "Other"

    db_expense = Expense(
        amount=expense.amount,
        description=expense.description,
        category=category or "Other",
        user_id=current_user_id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_user_expenses(db: Session):
    return db.query(Expense).filter(Expense.user_id == current_user_id).order_by(Expense.date.desc()).all()
