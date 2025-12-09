from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.entities.minute_summary import MinuteSummary
from src.domain.repositories.minute_summary_repository import MinuteSummaryRepository
from src.infrastructure.persistence.models.minute_summary_model import MinuteSummaryModel

class MinuteSummaryRepositoryImpl(MinuteSummaryRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, summary: MinuteSummary) -> MinuteSummary:
        db_summary = MinuteSummaryModel(
            summary_id=summary.summary_id,
            session_id=summary.session_id,
            activity_uuid=summary.activity_uuid,
            minute_number=summary.minute_number,
            timestamp=summary.timestamp,
            predominant_emotion=summary.predominant_emotion,
            emotion_confidence_avg=summary.emotion_confidence_avg,
            ear_avg=summary.ear_avg,
            pitch_avg=summary.pitch_avg,
            yaw_avg=summary.yaw_avg,
            looking_screen_percentage=summary.looking_screen_percentage,
            face_detected_percentage=summary.face_detected_percentage,
            distraction_count=summary.distraction_count,
            drowsiness_count=summary.drowsiness_count,
            abrupt_changes_count=summary.abrupt_changes_count,
            cognitive_state=summary.cognitive_state,
            engagement_level=summary.engagement_level
        )
        self.db.add(db_summary)
        self.db.commit()
        self.db.refresh(db_summary)
        
        return MinuteSummary(
            summary_id=db_summary.summary_id,
            session_id=db_summary.session_id,
            activity_uuid=db_summary.activity_uuid,
            minute_number=db_summary.minute_number,
            timestamp=db_summary.timestamp,
            predominant_emotion=db_summary.predominant_emotion,
            emotion_confidence_avg=db_summary.emotion_confidence_avg,
            ear_avg=db_summary.ear_avg,
            pitch_avg=db_summary.pitch_avg,
            yaw_avg=db_summary.yaw_avg,
            looking_screen_percentage=db_summary.looking_screen_percentage,
            face_detected_percentage=db_summary.face_detected_percentage,
            distraction_count=db_summary.distraction_count,
            drowsiness_count=db_summary.drowsiness_count,
            abrupt_changes_count=db_summary.abrupt_changes_count,
            cognitive_state=db_summary.cognitive_state,
            engagement_level=db_summary.engagement_level,
            created_at=db_summary.created_at.isoformat()
        )
    
    def get_by_id(self, summary_id: str) -> Optional[MinuteSummary]:
        db_summary = self.db.query(MinuteSummaryModel).filter(MinuteSummaryModel.summary_id == summary_id).first()
        
        if not db_summary:
            return None
        
        return MinuteSummary(
            summary_id=db_summary.summary_id,
            session_id=db_summary.session_id,
            activity_uuid=db_summary.activity_uuid,
            minute_number=db_summary.minute_number,
            timestamp=db_summary.timestamp,
            predominant_emotion=db_summary.predominant_emotion,
            emotion_confidence_avg=db_summary.emotion_confidence_avg,
            ear_avg=db_summary.ear_avg,
            pitch_avg=db_summary.pitch_avg,
            yaw_avg=db_summary.yaw_avg,
            looking_screen_percentage=db_summary.looking_screen_percentage,
            face_detected_percentage=db_summary.face_detected_percentage,
            distraction_count=db_summary.distraction_count,
            drowsiness_count=db_summary.drowsiness_count,
            abrupt_changes_count=db_summary.abrupt_changes_count,
            cognitive_state=db_summary.cognitive_state,
            engagement_level=db_summary.engagement_level,
            created_at=db_summary.created_at.isoformat()
        )
    
    def get_by_activity(self, activity_uuid: str) -> List[MinuteSummary]:
        db_summaries = self.db.query(MinuteSummaryModel).filter(
            MinuteSummaryModel.activity_uuid == activity_uuid
        ).order_by(MinuteSummaryModel.minute_number).all()
        
        return [
            MinuteSummary(
                summary_id=db_summary.summary_id,
                session_id=db_summary.session_id,
                activity_uuid=db_summary.activity_uuid,
                minute_number=db_summary.minute_number,
                timestamp=db_summary.timestamp,
                predominant_emotion=db_summary.predominant_emotion,
                emotion_confidence_avg=db_summary.emotion_confidence_avg,
                ear_avg=db_summary.ear_avg,
                pitch_avg=db_summary.pitch_avg,
                yaw_avg=db_summary.yaw_avg,
                looking_screen_percentage=db_summary.looking_screen_percentage,
                face_detected_percentage=db_summary.face_detected_percentage,
                distraction_count=db_summary.distraction_count,
                drowsiness_count=db_summary.drowsiness_count,
                abrupt_changes_count=db_summary.abrupt_changes_count,
                cognitive_state=db_summary.cognitive_state,
                engagement_level=db_summary.engagement_level,
                created_at=db_summary.created_at.isoformat()
            )
            for db_summary in db_summaries
        ]