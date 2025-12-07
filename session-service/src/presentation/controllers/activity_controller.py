from sqlalchemy.orm import Session
from src.application.dtos.activity_dto import StartActivityRequest, CompleteActivityRequest
from src.application.use_cases.activity.start_activity import StartActivityUseCase
from src.application.use_cases.activity.complete_activity import CompleteActivityUseCase
from src.application.use_cases.activity.abandon_activity import AbandonActivityUseCase
from src.application.use_cases.activity.pause_activity import PauseActivityUseCase
from src.application.use_cases.activity.resume_activity import ResumeActivityUseCase
from src.infrastructure.persistence.repositories.activity_repository_impl import ActivityRepositoryImpl
from src.infrastructure.persistence.repositories.pause_counter_repository_impl import PauseCounterRepositoryImpl

class ActivityController:
    
    @staticmethod
    def start_activity(session_id: str, request: StartActivityRequest, db: Session) -> dict:
        activity_repo = ActivityRepositoryImpl(db)
        use_case = StartActivityUseCase(activity_repo)
        return use_case.execute(session_id, request.external_activity_id, request.title, request.activity_type)
    
    @staticmethod
    def complete_activity(activity_uuid: str, request: CompleteActivityRequest, db: Session) -> dict:
        activity_repo = ActivityRepositoryImpl(db)
        pause_counter_repo = PauseCounterRepositoryImpl(db)
        use_case = CompleteActivityUseCase(activity_repo, pause_counter_repo)
        return use_case.execute(activity_uuid, request.feedback)
    
    @staticmethod
    def abandon_activity(activity_uuid: str, db: Session) -> dict:
        activity_repo = ActivityRepositoryImpl(db)
        pause_counter_repo = PauseCounterRepositoryImpl(db)
        use_case = AbandonActivityUseCase(activity_repo, pause_counter_repo)
        return use_case.execute(activity_uuid)
    
    @staticmethod
    def pause_activity(activity_uuid: str, db: Session) -> dict:
        activity_repo = ActivityRepositoryImpl(db)
        pause_counter_repo = PauseCounterRepositoryImpl(db)
        use_case = PauseActivityUseCase(activity_repo, pause_counter_repo)
        return use_case.execute(activity_uuid)
    
    @staticmethod
    def resume_activity(activity_uuid: str, db: Session) -> dict:
        activity_repo = ActivityRepositoryImpl(db)
        use_case = ResumeActivityUseCase(activity_repo)
        return use_case.execute(activity_uuid)