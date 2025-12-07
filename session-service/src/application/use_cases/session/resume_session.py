from src.domain.repositories.session_repository import SessionRepository

class ResumeSessionUseCase:
    
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo
    
    def execute(self, session_id: str) -> dict:
        session = self.session_repo.get_by_id(session_id)
        if not session:
            return {"error": "Sesión no encontrada"}
        session.resume()
        self.session_repo.update(session)
        print(f"\n[USE_CASE] Sesión reanudada: {session_id}\n")
        return {"status": "active"}