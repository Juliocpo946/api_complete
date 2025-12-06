from typing import Optional
from sqlalchemy.orm import Session
from src.domain.entities.activity import Activity
from src.domain.repositories.activity_repository import ActivityRepository
from src.infrastructure.persistence.models.activity_model import ActivityModel

class ActivityRepositoryImpl(ActivityRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, activity: Activity) -> Activity:
        db_activity = ActivityModel(
            activity_uuid=activity.activity_uuid,
            session_id=activity.session_id,
            external_activity_id=activity.external_activity_id,
            title=activity.title,
            activity_type=activity.activity_type,
            status=activity.status,
            pause_count=activity.pause_count
        )
        self.db.add(db_activity)
        self.db.commit()
        self.db.refresh(db_activity)
        print(f"\n[REPO] Actividad creada: {activity.activity_uuid}\n")
        
        return Activity(
            activity_uuid=db_activity.activity_uuid,
            session_id=db_activity.session_id,
            external_activity_id=db_activity.external_activity_id,
            title=db_activity.title,
            activity_type=db_activity.activity_type,
            status=db_activity.status,
            started_at=db_activity.started_at.isoformat(),
            completed_at=db_activity.completed_at.isoformat() if db_activity.completed_at else None,
            pause_count=db_activity.pause_count
        )
    
    def get_by_uuid(self, activity_uuid: str) -> Optional[Activity]:
        db_activity = self.db.query(ActivityModel).filter(ActivityModel.activity_uuid == activity_uuid).first()
        
        if not db_activity:
            return None
        
        return Activity(
            activity_uuid=db_activity.activity_uuid,
            session_id=db_activity.session_id,
            external_activity_id=db_activity.external_activity_id,
            title=db_activity.title,
            activity_type=db_activity.activity_type,
            status=db_activity.status,
            started_at=db_activity.started_at.isoformat(),
            completed_at=db_activity.completed_at.isoformat() if db_activity.completed_at else None,
            pause_count=db_activity.pause_count
        )
    
    def get_by_external_id(self, session_id: str, external_id: int) -> Optional[Activity]:
        db_activity = self.db.query(ActivityModel).filter(
            ActivityModel.session_id == session_id,
            ActivityModel.external_activity_id == external_id
        ).first()
        
        if not db_activity:
            return None
        
        return Activity(
            activity_uuid=db_activity.activity_uuid,
            session_id=db_activity.session_id,
            external_activity_id=db_activity.external_activity_id,
            title=db_activity.title,
            activity_type=db_activity.activity_type,
            status=db_activity.status,
            started_at=db_activity.started_at.isoformat(),
            completed_at=db_activity.completed_at.isoformat() if db_activity.completed_at else None,
            pause_count=db_activity.pause_count
        )
    
    def update(self, activity: Activity) -> Activity:
        db_activity = self.db.query(ActivityModel).filter(ActivityModel.activity_uuid == activity.activity_uuid).first()
        
        if not db_activity:
            return None
        
        db_activity.status = activity.status
        db_activity.pause_count = activity.pause_count
        db_activity.completed_at = activity.completed_at
        
        self.db.commit()
        self.db.refresh(db_activity)
        print(f"\n[REPO] Actividad actualizada: {activity.activity_uuid} -> {activity.status}\n")
        
        return Activity(
            activity_uuid=db_activity.activity_uuid,
            session_id=db_activity.session_id,
            external_activity_id=db_activity.external_activity_id,
            title=db_activity.title,
            activity_type=db_activity.activity_type,
            status=db_activity.status,
            started_at=db_activity.started_at.isoformat(),
            completed_at=db_activity.completed_at.isoformat() if db_activity.completed_at else None,
            pause_count=db_activity.pause_count
        )