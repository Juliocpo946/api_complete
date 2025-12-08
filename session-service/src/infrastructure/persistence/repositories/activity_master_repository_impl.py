from typing import Optional
from sqlalchemy.orm import Session
from src.domain.entities.activity_master import ActivityMaster
from src.domain.repositories.activity_master_repository import ActivityMasterRepository
from src.infrastructure.persistence.models.activity_master_model import ActivityMasterModel

class ActivityMasterRepositoryImpl(ActivityMasterRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_or_update(self, activity_master: ActivityMaster) -> ActivityMaster:
        db_master = self.db.query(ActivityMasterModel).filter(
            ActivityMasterModel.external_activity_id == activity_master.external_activity_id
        ).first()
        
        if db_master:
            db_master.title = activity_master.title
            db_master.subtitle = activity_master.subtitle
            db_master.content = activity_master.content
            db_master.activity_type = activity_master.activity_type
            print(f"\n[REPO] Actividad Master actualizada: {activity_master.external_activity_id}\n")
        else:
            # Crear si no existe
            db_master = ActivityMasterModel(
                external_activity_id=activity_master.external_activity_id,
                title=activity_master.title,
                subtitle=activity_master.subtitle,
                content=activity_master.content,
                activity_type=activity_master.activity_type
            )
            self.db.add(db_master)
            print(f"\n[REPO] Actividad Master creada: {activity_master.external_activity_id}\n")
        
        self.db.commit()
        self.db.refresh(db_master)
        
        return ActivityMaster(
            external_activity_id=db_master.external_activity_id,
            title=db_master.title,
            subtitle=db_master.subtitle,
            content=db_master.content,
            activity_type=db_master.activity_type
        )
    
    def get_by_id(self, external_activity_id: int) -> Optional[ActivityMaster]:
        db_master = self.db.query(ActivityMasterModel).filter(
            ActivityMasterModel.external_activity_id == external_activity_id
        ).first()
        
        if not db_master:
            return None
        
        return ActivityMaster(
            external_activity_id=db_master.external_activity_id,
            title=db_master.title,
            subtitle=db_master.subtitle,
            content=db_master.content,
            activity_type=db_master.activity_type
        )