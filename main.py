from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import google.generativeai as genai
from config.settings import config
import tempfile
import os

# Use a temporary directory for the database to avoid permission issues
db_dir = os.path.join(tempfile.gettempdir(), "finance_app")
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "finance_app.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL debugging
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    expenses = relationship("Expense", back_populates="owner")
    budgets = relationship("Budget", back_populates="owner")

class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    description = Column(String)
    category = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="expenses")

class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    amount = Column(Float)
    month = Column(String)  # Format: "2024-01"
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="budgets")

# Create tables with error handling
try:
    Base.metadata.create_all(bind=engine)
    print(f"Database created at: {db_path}")
except Exception as e:
    print(f"Error creating database: {e}")
    # Try alternative location
    SQLALCHEMY_DATABASE_URL = "sqlite:///finance_app_temp.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Using fallback database location")

# Pydantic models
class ExpenseCreate(BaseModel):
    amount: float
    description: str
    category: Optional[str] = None

class ExpenseResponse(BaseModel):
    id: int
    amount: float
    description: str
    category: str
    date: datetime
    
    class Config:
        from_attributes = True

class BudgetCreate(BaseModel):
    category: str
    amount: float
    month: str

class BudgetResponse(BaseModel):
    id: int
    category: str
    amount: float
    month: str
    
    class Config:
        from_attributes = True

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    insights: Optional[dict] = None

# FastAPI app
app = FastAPI(title="Personal Finance Mentor API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","https://fm-backend-oajp.onrender.com/"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google AI
api_key = config["GOOGLE_AI_API_KEY"]
if not api_key:
    print("GOOGLE_AI_API_KEY not found in environment variables")
    model = None
else:
    try:
        genai.configure(api_key=api_key)
        
        # Try different model names that are currently available
        model_names = [
            'gemini-2.5-flash',
            'gemini-2.5-pro',
            'gemini-1.0-pro'
        ]

        # for m in genai.list_models():
        #     print(m.name)
        
        model = None
        for model_name in model_names:
            try:
                test_model = genai.GenerativeModel(model_name)
                test_response = test_model.generate_content("Hello")
                print(f"Success with {model_name}: {test_response.text[:50]}...")
                model = test_model
                break
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                continue
        
        if model:
            print("Google AI configured successfully")
        else:
            print("All model attempts failed")
    except Exception as e:
        print(f"Error configuring Google AI: {e}")
        model = None


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple user session (for MVP - no real auth)
current_user_id = 1  # Hardcoded for MVP

# Ensure default user exists
def ensure_default_user(db: Session):
    try:
        user = db.query(User).filter(User.id == current_user_id).first()
        if not user:
            user = User(id=current_user_id, username="demo_user")
            db.add(user)
            db.commit()
        return user
    except Exception as e:
        print(f"Database error: {e}")
        db.rollback()
        # Try to get existing user
        user = db.query(User).filter(User.id == current_user_id).first()
        if user:
            return user
        raise HTTPException(status_code=500, detail="Database initialization failed")

# Routes
@app.get("/")
def read_root():
    return {"message": "Personal Finance Mentor API"}

@app.post("/expenses", response_model=ExpenseResponse)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    ensure_default_user(db)
    
    # Auto-categorize using AI if category not provided
    category = expense.category
    if not category:
        try:
            prompt = f"Categorize this expense into one of these categories: Food, Transportation, Entertainment, Shopping, Bills, Other. Expense: '{expense.description} ${expense.amount}'. Respond with only the category name."
            response = model.generate_content(prompt)
            category = response.text.strip()
        except:
            category = "Other"
    
    db_expense = Expense(
        amount=expense.amount,
        description=expense.description,
        category=category,
        user_id=current_user_id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.get("/expenses", response_model=List[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db)):
    ensure_default_user(db)
    expenses = db.query(Expense).filter(Expense.user_id == current_user_id).order_by(Expense.date.desc()).all()
    return expenses

@app.post("/budgets", response_model=BudgetResponse)
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

@app.get("/budgets", response_model=List[BudgetResponse])
def get_budgets(db: Session = Depends(get_db)):
    ensure_default_user(db)
    budgets = db.query(Budget).filter(Budget.user_id == current_user_id).all()
    return budgets

@app.post("/chat", response_model=ChatResponse)
def chat_with_ai(message: ChatMessage, db: Session = Depends(get_db)):
    ensure_default_user(db)
    
    try:
        # Get user's financial data for context
        expenses = db.query(Expense).filter(Expense.user_id == current_user_id).all()
        print(f"Expenses for user {current_user_id}: {expenses}")
        budgets = db.query(Budget).filter(Budget.user_id == current_user_id).all()
        print(f"Budgets for user {current_user_id}: {budgets}")
        if not expenses and not budgets:
            return ChatResponse(response="You have no financial data yet. Please add some expenses or budgets first.")
        print(f"User message: {message.message}")

        # Calculate basic insights
        current_month = datetime.now().strftime("%Y-%m")
        monthly_expenses = [e for e in expenses if e.date.strftime("%Y-%m") == current_month]
        total_spent = sum(e.amount for e in monthly_expenses)

        # Create context for AI
        context = f"""
        User's Financial Context:
        - Total spent this month: ${total_spent:.2f}
        - Number of transactions this month: {len(monthly_expenses)}
        - Recent expenses: {[f"{e.category}: ${e.amount} ({e.description})" for e in monthly_expenses[-5:]]}
        - Active budgets: {[f"{b.category}: ${b.amount}" for b in budgets]}
        
        User Question: {message.message}
        
        Please provide helpful, personalized financial advice based on their data. Keep responses concise and actionable.
        """
        
        response = model.generate_content(context)
        print(f"AI response: {response.text}")
        
        insights = {
            "total_spent_this_month": total_spent,
            "transaction_count": len(monthly_expenses),
            "top_category": max(set(e.category for e in monthly_expenses), 
                              key=lambda x: sum(e.amount for e in monthly_expenses if e.category == x)) 
                          if monthly_expenses else "None"
        }

        print(f"Insights: {insights}")
        
        return ChatResponse(response=response.text, insights=insights)
    
    except Exception as e:
        return ChatResponse(response="I'm having trouble accessing the AI service right now. Please try again later.")

@app.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    ensure_default_user(db)
    
    current_month = datetime.now().strftime("%Y-%m")
    monthly_expenses = db.query(Expense).filter(
        Expense.user_id == current_user_id,
        Expense.date >= datetime.now().replace(day=1)
    ).all()
    
    # Calculate spending by category
    spending_by_category = {}
    for expense in monthly_expenses:
        spending_by_category[expense.category] = spending_by_category.get(expense.category, 0) + expense.amount
    
    total_spent = sum(expense.amount for expense in monthly_expenses)
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)