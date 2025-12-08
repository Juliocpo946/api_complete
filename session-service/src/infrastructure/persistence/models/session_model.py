from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.persistence.database import Base

class SessionModel(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String(255), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    disability_type = Column(String(100), nullable=False)
    cognitive_analysis_enabled = Column(Boolean, default=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    user_activities = relationship("UserActivityModel", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SessionModel(session_id={self.session_id}, user_id={self.user_id}, status={self.status})>"