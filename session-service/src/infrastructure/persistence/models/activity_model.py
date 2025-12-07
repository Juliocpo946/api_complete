from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.persistence.database import Base

class ActivityModel(Base):
    __tablename__ = "activities"
    
    activity_uuid = Column(String(255), primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("sessions.session_id"), nullable=False)
    external_activity_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    activity_type = Column(String(100), nullable=False)
    status = Column(String(50), default="in_progress")
    pause_count = Column(Integer, default=0)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    session = relationship("SessionModel", back_populates="activities")
    pause_counters = relationship("PauseCounterModel", back_populates="activity", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ActivityModel(activity_uuid={self.activity_uuid}, title={self.title}, status={self.status})>"
