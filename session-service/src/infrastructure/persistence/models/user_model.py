from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from src.infrastructure.persistence.database import Base

class UserModel(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    settings = Column(JSON, default={
        "cognitive_analysis_enabled": True,
        "text_notifications": True,
        "video_suggestions": True,
        "vibration_alerts": True,
        "pause_suggestions": False
    })
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<UserModel(user_id={self.user_id}, updated_at={self.updated_at})>"

