from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    amount = Column(Float)
    month = Column(String)  # Format: "2024-01"
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="budgets")
