from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from src.infrastructure.persistence.database import Base

class FrameModel(Base):
    __tablename__ = "frames"
    
    frame_id = Column(String(255), primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    activity_uuid = Column(String(255), nullable=False, index=True)
    timestamp = Column(String(50), nullable=False)
    sentiment_analysis = Column(JSON, default={})
    biometric_data = Column(JSON, default={})
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<FrameModel(frame_id={self.frame_id}, activity_uuid={self.activity_uuid})>"