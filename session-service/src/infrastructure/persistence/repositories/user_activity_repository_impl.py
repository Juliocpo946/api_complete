from typing import Optional
from sqlalchemy.orm import Session
from src.domain.entities.user_activity import UserActivity
from src.domain.repositories.user_activity_repository import UserActivityRepository
from src.infrastructure.persistence.models.user_activity_model import UserActivityModel

class UserActivityRepositoryImpl(UserActivityRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_activity: UserActivity) -> UserActivity:
        db_activity = UserActivityModel(
            activity_uuid=user_activity.activity_uuid,
            session_id=user_activity.session_id,
            external_activity_id=user_activity.external_activity_id,
            status=user_activity.status,
            pause_count=user_activity.pause_count
        )
        self.db.add(db_activity)
        self.db.commit()
        self.db.refresh(db_activity)
        print(f"\n[REPO] User Activity creada: {user_activity.activity_uuid}\n")
        
        return UserActivity(
            activity_uuid=db_activity.activity_uuid,
            session_id=db_activity.session_id,
            external_activity_id=db_activity.external_activity_id,
            status=db_activity.status,
            started_at=db_activity.started_at.isoformat(),
            completed_at=db_activity.completed_at.isoformat() if db_activity.completed_at else None,
            pause_count=db_activity.pause_count
        )
    
    def get_by_uuid(self, activity_uuid: str) -> Optional[UserActivity]:
        db_activity = self.db.query(UserActivityModel).filter(UserActivityModel.activity_uuid == activity_uuid).first()
        
        if not db_activity:
            return None
        
        return UserActivity(
            activity_uuid=db_activity.activity_uuid,
            session_id=db_activity.session_id,
            external_activity_id=db_activity.external_activity_id,
            status=db_activity.status,
            started_at=db_activity.started_at.isoformat(),
            completed_at=db_activity.completed_at.isoformat() if db_activity.completed_at else None,
            pause_count=db_activity.pause_count
        )
    
    def get_by_external_id(self, session_id: str, external_id: int) -> Optional[UserActivity]:
        db_activity = self.db.query(UserActivityModel).filter(
            UserActivityModel.session_id == session_id,
            UserActivityModel.external_activity_id == external_id
        ).first()
        
        if not db_activity:
            return None
        
        return UserActivity(
            activity_uuid=db_activity.activity_uuid,
            session_id=db_activity.session_id,
            external_activity_id=db_activity.external_activity_id,
            status=db_activity.status,
            started_at=db_activity.started_at.isoformat(),
            completed_at=db_activity.completed_at.isoformat() if db_activity.completed_at else None,
            pause_count=db_activity.pause_count
        )
    
    def update(self, user_activity: UserActivity) -> UserActivity:
        db_activity = self.db.query(UserActivityModel).filter(UserActivityModel.activity_uuid == user_activity.activity_uuid).first()
        
        if not db_activity:
            return None
        
        db_activity.status = user_activity.status
        db_activity.pause_count = user_activity.pause_count
        db_activity.completed_at = user_activity.completed_at
        
        self.db.commit()
        self.db.refresh(db_activity)
        print(f"\n[REPO] User Activity actualizada: {user_activity.activity_uuid} -> {user_activity.status}\n")
        
        return UserActivity(
            activity_uuid=db_activity.activity_uuid,
            session_id=db_activity.session_id,
            external_activity_id=db_activity.external_activity_id,
            status=db_activity.status,
            started_at=db_activity.started_at.isoformat(),
            completed_at=db_activity.completed_at.isoformat() if db_activity.completed_at else None,
            pause_count=db_activity.pause_count
        )