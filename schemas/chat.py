from pydantic import BaseModel
from typing import Optional

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    insights: Optional[dict] = None
