from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import Base, engine
from config.settings import config
from api import route_expenses, route_budgets, routes_chat

Base.metadata.create_all(bind=engine)

app = FastAPI(title=config["PROJECT_NAME"])

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(route_expenses.router, prefix="/expenses", tags=["Expenses"])
app.include_router(route_budgets.router, prefix="/budgets", tags=["Budgets"])
app.include_router(routes_chat.router, prefix="/chat", tags=["Chat"])

@app.get("/")
def root():
    return {"message": "Personal Finance Mentor API"}
