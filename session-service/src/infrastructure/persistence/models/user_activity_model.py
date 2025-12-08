from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.persistence.database import Base

class UserActivityModel(Base):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    activity_uuid = Column(String(255), unique=True, nullable=False, index=True)
    session_id = Column(String(255), ForeignKey("sessions.session_id"), nullable=False)
    external_activity_id = Column(Integer, ForeignKey("activity_masters.external_activity_id"), nullable=False)
    status = Column(String(50), default="in_progress")
    pause_count = Column(Integer, default=0)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    session = relationship("SessionModel", back_populates="user_activities")
    activity_master = relationship("ActivityMasterModel")
    pause_counters = relationship("PauseCounterModel", back_populates="user_activity", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UserActivityModel(activity_uuid={self.activity_uuid}, external_id={self.external_activity_id}, status={self.status})>"