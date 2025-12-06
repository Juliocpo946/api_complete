from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.entities.intervention import Intervention
from src.domain.repositories.intervention_repository import InterventionRepository
from src.infrastructure.persistence.models.intervention_model import InterventionModel

class InterventionRepositoryImpl(InterventionRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, intervention: Intervention) -> Intervention:
        db_intervention = InterventionModel(
            packet_id=intervention.packet_id,
            session_id=intervention.session_id,
            activity_uuid=intervention.activity_uuid,
            intervention_type=intervention.intervention_type,
            video_url=intervention.video_url,
            display_text=intervention.display_text,
            vibration_enabled=intervention.vibration_enabled,
            metric_name=intervention.metric_name,
            metric_value=int(intervention.metric_value * 100),
            confidence=int(intervention.confidence * 100),
            duration_ms=intervention.duration_ms
        )
        self.db.add(db_intervention)
        self.db.commit()
        self.db.refresh(db_intervention)
        
        print(f"\n[REPO] Intervención guardada: {intervention.packet_id}\n")
        
        return Intervention(
            packet_id=db_intervention.packet_id,
            session_id=db_intervention.session_id,
            activity_uuid=db_intervention.activity_uuid,
            intervention_type=db_intervention.intervention_type,
            video_url=db_intervention.video_url,
            display_text=db_intervention.display_text,
            vibration_enabled=db_intervention.vibration_enabled,
            metric_name=db_intervention.metric_name,
            metric_value=db_intervention.metric_value / 100,
            confidence=db_intervention.confidence / 100,
            duration_ms=db_intervention.duration_ms,
            timestamp=db_intervention.timestamp.isoformat()
        )
    
    def get_by_id(self, packet_id: str) -> Optional[Intervention]:
        db_intervention = self.db.query(InterventionModel).filter(InterventionModel.packet_id == packet_id).first()
        
        if not db_intervention:
            return None
        
        return Intervention(
            packet_id=db_intervention.packet_id,
            session_id=db_intervention.session_id,
            activity_uuid=db_intervention.activity_uuid,
            intervention_type=db_intervention.intervention_type,
            video_url=db_intervention.video_url,
            display_text=db_intervention.display_text,
            vibration_enabled=db_intervention.vibration_enabled,
            metric_name=db_intervention.metric_name,
            metric_value=db_intervention.metric_value / 100,
            confidence=db_intervention.confidence / 100,
            duration_ms=db_intervention.duration_ms,
            timestamp=db_intervention.timestamp.isoformat()
        )
    
    def get_by_activity(self, activity_uuid: str) -> List[Intervention]:
        db_interventions = self.db.query(InterventionModel).filter(InterventionModel.activity_uuid == activity_uuid).all()
        
        return [
            Intervention(
                packet_id=db_intervention.packet_id,
                session_id=db_intervention.session_id,
                activity_uuid=db_intervention.activity_uuid,
                intervention_type=db_intervention.intervention_type,
                video_url=db_intervention.video_url,
                display_text=db_intervention.display_text,
                vibration_enabled=db_intervention.vibration_enabled,
                metric_name=db_intervention.metric_name,
                metric_value=db_intervention.metric_value / 100,
                confidence=db_intervention.confidence / 100,
                duration_ms=db_intervention.duration_ms,
                timestamp=db_intervention.timestamp.isoformat()
            )
            for db_intervention in db_interventions
        ]