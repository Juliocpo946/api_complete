from datetime import datetime
from src.domain.entities.session import Session
from src.domain.repositories.session_repository import SessionRepository
from src.domain.repositories.user_repository import UserRepository

class CreateSessionUseCase:
    
    def __init__(self, session_repo: SessionRepository, user_repo: UserRepository):
        self.session_repo = session_repo
        self.user_repo = user_repo
    
    def execute(self, user_id: int, disability_type: str, cognitive_enabled: bool) -> dict:
        user = self.user_repo.get_by_id(user_id)
        
        session_id = f"sess_{datetime.now().timestamp()}"
        session = Session(
            session_id=session_id,
            user_id=user_id,
            disability_type=disability_type,
            cognitive_analysis_enabled=cognitive_enabled
        )
        self.session_repo.create(session)
        print(f"\n{'='*60}")
        print(f"[USE_CASE] Sesión creada")
        print(f"{'='*60}")
        print(f"Session ID: {session_id}")
        print(f"Usuario: {user_id}")
        print(f"Tipo Discapacidad: {disability_type}")
        print(f"Análisis Cognitivo: {cognitive_enabled}")
        print(f"{'='*60}\n")
        return {"session_id": session_id, "status": "active"}