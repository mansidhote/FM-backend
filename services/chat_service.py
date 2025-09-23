from datetime import datetime
from sqlalchemy.orm import Session
from utils.dependencies import current_user_id
from models.expense import Expense
from models.budget import Budget
from schemas.chat import ChatResponse
from app.ai import model

def chat_with_ai_service(user_message: str, db: Session):
    # Ensure user data
    expenses = db.query(Expense).filter(Expense.user_id == current_user_id).all()
    budgets = db.query(Budget).filter(Budget.user_id == current_user_id).all()

    if not expenses and not budgets:
        return ChatResponse(response="You have no financial data yet. Please add some expenses or budgets first.")

    current_month = datetime.now().strftime("%Y-%m")
    monthly_expenses = [e for e in expenses if e.date.strftime("%Y-%m") == current_month]
    total_spent = sum(e.amount for e in monthly_expenses)

    context = f"""
    User's Financial Context:
    - Total spent this month: ${total_spent:.2f}
    - Number of transactions this month: {len(monthly_expenses)}
    - Recent expenses: {[f"{e.category}: ${e.amount} ({e.description})" for e in monthly_expenses[-5:]]}
    - Active budgets: {[f"{b.category}: ${b.amount}" for b in budgets]}

    User Question: {user_message}

    Please provide helpful, personalized financial advice based on their data. Keep responses concise and actionable.
    """

    try:
        response = model.generate_content(context) if model else None
        reply_text = response.text if response else "AI service unavailable."

        insights = {
            "total_spent_this_month": total_spent,
            "transaction_count": len(monthly_expenses),
            "top_category": max(set(e.category for e in monthly_expenses),
                                key=lambda x: sum(e.amount for e in monthly_expenses if e.category == x))
                          if monthly_expenses else "None"
        }

        return ChatResponse(response=reply_text, insights=insights)

    except Exception:
        return ChatResponse(response="I'm having trouble accessing the AI service right now. Please try again later.")
