from src.domain.repositories.session_repository import SessionRepository

class FinalizeSessionUseCase:
    
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo
    
    def execute(self, session_id: str) -> dict:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            return {"error": "Sesión no encontrada"}
        session.finalize()
        self.session_repo.delete(session_id)
        print(f"\n[USE_CASE] Sesión finalizada: {session_id}\n")
        return {"status": "finalized"}