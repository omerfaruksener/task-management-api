from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime
from app.db.session import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="todo")
    priority = Column(String, default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))