from typing import Optional
from sqlalchemy.orm import Session
from src.domain.entities.session import Session as SessionEntity
from src.domain.repositories.session_repository import SessionRepository
from src.infrastructure.persistence.models.session_model import SessionModel

class SessionRepositoryImpl(SessionRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, session: SessionEntity) -> SessionEntity:
        db_session = SessionModel(
            session_id=session.session_id,
            user_id=session.user_id,
            disability_type=session.disability_type,
            cognitive_analysis_enabled=session.cognitive_analysis_enabled,
            status=session.status
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        print(f"\n[REPO] Sesión creada: {session.session_id}\n")
        
        return SessionEntity(
            session_id=db_session.session_id,
            user_id=db_session.user_id,
            disability_type=db_session.disability_type,
            cognitive_analysis_enabled=db_session.cognitive_analysis_enabled,
            status=db_session.status,
            created_at=db_session.created_at.isoformat()
        )
    
    def get_by_id(self, session_id: str) -> Optional[SessionEntity]:
        db_session = self.db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        
        if not db_session:
            return None
        
        return SessionEntity(
            session_id=db_session.session_id,
            user_id=db_session.user_id,
            disability_type=db_session.disability_type,
            cognitive_analysis_enabled=db_session.cognitive_analysis_enabled,
            status=db_session.status,
            created_at=db_session.created_at.isoformat()
        )
    
    def update(self, session: SessionEntity) -> SessionEntity:
        db_session = self.db.query(SessionModel).filter(SessionModel.session_id == session.session_id).first()
        
        if not db_session:
            return None
        
        db_session.status = session.status
        self.db.commit()
        self.db.refresh(db_session)
        print(f"\n[REPO] Sesión actualizada: {session.session_id} -> {session.status}\n")
        
        return SessionEntity(
            session_id=db_session.session_id,
            user_id=db_session.user_id,
            disability_type=db_session.disability_type,
            cognitive_analysis_enabled=db_session.cognitive_analysis_enabled,
            status=db_session.status,
            created_at=db_session.created_at.isoformat()
        )
    
    def delete(self, session_id: str) -> bool:
        db_session = self.db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        
        if not db_session:
            return False
        
        self.db.delete(db_session)
        self.db.commit()
        print(f"\n[REPO] Sesión eliminada: {session_id}\n")
        return True