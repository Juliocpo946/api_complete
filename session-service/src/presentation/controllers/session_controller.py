from sqlalchemy.orm import Session
from src.application.dtos.session_dto import CreateSessionRequest
from src.application.use_cases.session.create_session import CreateSessionUseCase
from src.application.use_cases.session.pause_session import PauseSessionUseCase
from src.application.use_cases.session.resume_session import ResumeSessionUseCase
from src.application.use_cases.session.finalize_session import FinalizeSessionUseCase
from src.infrastructure.persistence.repositories.session_repository_impl import SessionRepositoryImpl
from src.infrastructure.persistence.repositories.user_repository_impl import UserRepositoryImpl

class SessionController:
    
    @staticmethod
    def create_session(request: CreateSessionRequest, db: Session) -> dict:
        session_repo = SessionRepositoryImpl(db)
        user_repo = UserRepositoryImpl(db)
        use_case = CreateSessionUseCase(session_repo, user_repo)
        return use_case.execute(request.user_id, request.disability_type, request.cognitive_analysis_enabled)
    
    @staticmethod
    def pause_session(session_id: str, db: Session) -> dict:
        session_repo = SessionRepositoryImpl(db)
        use_case = PauseSessionUseCase(session_repo)
        return use_case.execute(session_id)
    
    @staticmethod
    def resume_session(session_id: str, db: Session) -> dict:
        session_repo = SessionRepositoryImpl(db)
        use_case = ResumeSessionUseCase(session_repo)
        return use_case.execute(session_id)
    
    @staticmethod
    def finalize_session(session_id: str, db: Session) -> dict:
        session_repo = SessionRepositoryImpl(db)
        use_case = FinalizeSessionUseCase(session_repo)
        return use_case.execute(session_id)