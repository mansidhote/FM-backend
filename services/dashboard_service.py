from datetime import datetime
from sqlalchemy.orm import Session
from utils.dependencies import current_user_id
from models.expense import Expense

def get_dashboard_service(db: Session):
    current_month = datetime.now().strftime("%Y-%m")
    monthly_expenses = db.query(Expense).filter(
        Expense.user_id == current_user_id,
        Expense.date >= datetime.now().replace(day=1)
    ).all()

    spending_by_category = {}
    for expense in monthly_expenses:
        spending_by_category[expense.category] = spending_by_category.get(expense.category, 0) + expense.amount

    total_spent = sum(exp.amount for exp in monthly_expenses)

    return {
        "total_spent": total_spent,
        "transaction_count": len(monthly_expenses),
        "spending_by_category": spending_by_category,
        "recent_expenses": [
            {
                "description": e.description,
                "amount": e.amount,
                "category": e.category,
                "date": e.date.isoformat()
            } for e in sorted(monthly_expenses, key=lambda x: x.date, reverse=True)[:5]
        ]
    }
