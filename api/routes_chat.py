from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from schemas.chat import ChatMessage, ChatResponse
from services.chat_service import chat_with_ai_service
from utils.dependencies import get_db, ensure_default_user

router = APIRouter()

@router.post("/", response_model=ChatResponse)
def chat_with_ai(message: ChatMessage, db: Session = Depends(get_db)):
    ensure_default_user(db)
    return chat_with_ai_service(message.message, db)
