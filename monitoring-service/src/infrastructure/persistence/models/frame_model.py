from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from src.infrastructure.persistence.database import Base

class InterventionModel(Base):
    __tablename__ = "interventions"
    
    packet_id = Column(String(255), primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    activity_uuid = Column(String(255), nullable=False, index=True)
    intervention_type = Column(String(50), nullable=False)
    video_url = Column(String(500), nullable=True)
    display_text = Column(String(1000), nullable=True)
    vibration_enabled = Column(Boolean, default=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Integer, default=0)
    confidence = Column(Integer, default=0)
    duration_ms = Column(Integer, default=5000)
    timestamp = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<InterventionModel(packet_id={self.packet_id}, activity_uuid={self.activity_uuid})>"