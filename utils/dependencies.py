from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from config.database import SessionLocal
from models.user import User

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple MVP user session
current_user_id = 1

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
        user = db.query(User).filter(User.id == current_user_id).first()
        if user:
            return user
        raise HTTPException(status_code=500, detail="Database initialization failed")
