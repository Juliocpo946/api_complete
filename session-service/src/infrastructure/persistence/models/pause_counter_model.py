from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.persistence.database import Base

class PauseCounterModel(Base):
    __tablename__ = "pause_counters"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_uuid = Column(String(255), ForeignKey("activities.activity_uuid"), nullable=False)
    pause_count = Column(Integer, default=0)
    paused_timestamps = Column(JSON, default=[])
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    activity = relationship("ActivityModel", back_populates="pause_counters")
    
    def __repr__(self):
        return f"<PauseCounterModel(activity_uuid={self.activity_uuid}, pause_count={self.pause_count})>"