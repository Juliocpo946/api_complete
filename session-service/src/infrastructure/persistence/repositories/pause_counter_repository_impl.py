from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.entities.pause_counter import PauseCounter
from src.domain.repositories.pause_counter_repository import PauseCounterRepository
from src.infrastructure.persistence.models.pause_counter_model import PauseCounterModel

class PauseCounterRepositoryImpl(PauseCounterRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, pause_counter: PauseCounter) -> PauseCounter:
        db_pause_counter = PauseCounterModel(
            activity_uuid=pause_counter.activity_uuid,
            pause_count=pause_counter.count,
            paused_timestamps=pause_counter.paused_timestamps
        )
        self.db.add(db_pause_counter)
        self.db.commit()
        self.db.refresh(db_pause_counter)
        print(f"\n[REPO] Contador de pausas creado: {pause_counter.activity_uuid}\n")
        
        return PauseCounter(
            activity_uuid=db_pause_counter.activity_uuid,
            count=db_pause_counter.pause_count,
            paused_timestamps=db_pause_counter.paused_timestamps
        )
    
    def get_by_activity(self, activity_uuid: str) -> Optional[PauseCounter]:
        db_pause_counter = self.db.query(PauseCounterModel).filter(
            PauseCounterModel.activity_uuid == activity_uuid
        ).first()
        
        if not db_pause_counter:
            return None
        
        return PauseCounter(
            activity_uuid=db_pause_counter.activity_uuid,
            count=db_pause_counter.pause_count,
            paused_timestamps=db_pause_counter.paused_timestamps
        )
    
    def update(self, pause_counter: PauseCounter) -> PauseCounter:
        db_pause_counter = self.db.query(PauseCounterModel).filter(
            PauseCounterModel.activity_uuid == pause_counter.activity_uuid
        ).first()
        
        if not db_pause_counter:
            return None
        
        db_pause_counter.pause_count = pause_counter.count
        db_pause_counter.paused_timestamps = pause_counter.paused_timestamps
        
        self.db.commit()
        self.db.refresh(db_pause_counter)
        print(f"\n[REPO] Contador de pausas actualizado: {pause_counter.activity_uuid}\n")
        
        return PauseCounter(
            activity_uuid=db_pause_counter.activity_uuid,
            count=db_pause_counter.pause_count,
            paused_timestamps=db_pause_counter.paused_timestamps
        )
    
    def increment(self, activity_uuid: str, timestamp: str) -> PauseCounter:
        db_pause_counter = self.db.query(PauseCounterModel).filter(
            PauseCounterModel.activity_uuid == activity_uuid
        ).first()
        
        if not db_pause_counter:
            db_pause_counter = PauseCounterModel(
                activity_uuid=activity_uuid,
                pause_count=1,
                paused_timestamps=[timestamp]
            )
            self.db.add(db_pause_counter)
        else:
            db_pause_counter.pause_count += 1
            db_pause_counter.paused_timestamps.append(timestamp)
        
        self.db.commit()
        self.db.refresh(db_pause_counter)
        print(f"\n[REPO] Pausa incrementada para actividad: {activity_uuid} (Total: {db_pause_counter.pause_count})\n")
        
        return PauseCounter(
            activity_uuid=db_pause_counter.activity_uuid,
            count=db_pause_counter.pause_count,
            paused_timestamps=db_pause_counter.paused_timestamps
        )
    
    def delete(self, activity_uuid: str) -> bool:
        db_pause_counter = self.db.query(PauseCounterModel).filter(
            PauseCounterModel.activity_uuid == activity_uuid
        ).first()
        
        if not db_pause_counter:
            return False
        
        self.db.delete(db_pause_counter)
        self.db.commit()
        print(f"\n[REPO] Contador de pausas eliminado: {activity_uuid}\n")
        return True