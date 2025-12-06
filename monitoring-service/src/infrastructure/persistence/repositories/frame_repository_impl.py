from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.entities.frame import Frame
from src.domain.repositories.frame_repository import FrameRepository
from src.infrastructure.persistence.models.frame_model import FrameModel

class FrameRepositoryImpl(FrameRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, frame: Frame) -> Frame:
        db_frame = FrameModel(
            frame_id=frame.frame_id,
            session_id=frame.session_id,
            activity_uuid=frame.activity_uuid,
            timestamp=frame.timestamp,
            sentiment_analysis=frame.sentiment_analysis,
            biometric_data=frame.biometric_data
        )
        self.db.add(db_frame)
        self.db.commit()
        self.db.refresh(db_frame)
        
        return Frame(
            frame_id=db_frame.frame_id,
            session_id=db_frame.session_id,
            activity_uuid=db_frame.activity_uuid,
            timestamp=db_frame.timestamp,
            sentiment_analysis=db_frame.sentiment_analysis,
            biometric_data=db_frame.biometric_data,
            created_at=db_frame.created_at.isoformat()
        )
    
    def get_by_id(self, frame_id: str) -> Optional[Frame]:
        db_frame = self.db.query(FrameModel).filter(FrameModel.frame_id == frame_id).first()
        
        if not db_frame:
            return None
        
        return Frame(
            frame_id=db_frame.frame_id,
            session_id=db_frame.session_id,
            activity_uuid=db_frame.activity_uuid,
            timestamp=db_frame.timestamp,
            sentiment_analysis=db_frame.sentiment_analysis,
            biometric_data=db_frame.biometric_data,
            created_at=db_frame.created_at.isoformat()
        )
    
    def get_by_activity(self, activity_uuid: str) -> List[Frame]:
        db_frames = self.db.query(FrameModel).filter(FrameModel.activity_uuid == activity_uuid).all()
        
        return [
            Frame(
                frame_id=db_frame.frame_id,
                session_id=db_frame.session_id,
                activity_uuid=db_frame.activity_uuid,
                timestamp=db_frame.timestamp,
                sentiment_analysis=db_frame.sentiment_analysis,
                biometric_data=db_frame.biometric_data,
                created_at=db_frame.created_at.isoformat()
            )
            for db_frame in db_frames
        ]