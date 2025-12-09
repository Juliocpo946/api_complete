from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.sql import func
from src.infrastructure.persistence.database import Base

class MinuteSummaryModel(Base):
    __tablename__ = "minute_summaries"
    
    summary_id = Column(String(255), primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    activity_uuid = Column(String(255), nullable=False, index=True)
    minute_number = Column(Integer, nullable=False)
    timestamp = Column(String(50), nullable=False)
    
    predominant_emotion = Column(String(50), nullable=False)
    emotion_confidence_avg = Column(Float, default=0.0)
    
    ear_avg = Column(Float, default=0.0)
    pitch_avg = Column(Float, default=0.0)
    yaw_avg = Column(Float, default=0.0)
    
    looking_screen_percentage = Column(Float, default=0.0)
    face_detected_percentage = Column(Float, default=0.0)
    
    distraction_count = Column(Integer, default=0)
    drowsiness_count = Column(Integer, default=0)
    abrupt_changes_count = Column(Integer, default=0)
    
    cognitive_state = Column(String(50), nullable=False)
    engagement_level = Column(String(20), nullable=False)
    
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<MinuteSummaryModel(summary_id={self.summary_id}, activity_uuid={self.activity_uuid}, minute={self.minute_number})>"