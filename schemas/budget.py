from pydantic import BaseModel

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
