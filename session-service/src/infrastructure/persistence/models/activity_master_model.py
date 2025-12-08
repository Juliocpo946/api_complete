from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from src.infrastructure.persistence.database import Base

class ActivityMasterModel(Base):
    __tablename__ = "activity_masters"
    
    external_activity_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    activity_type = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<ActivityMasterModel(external_activity_id={self.external_activity_id}, title={self.title}, type={self.activity_type})>"