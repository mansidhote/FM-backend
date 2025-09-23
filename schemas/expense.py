from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
