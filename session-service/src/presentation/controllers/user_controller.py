from sqlalchemy.orm import Session
from src.application.dtos.user_dto import UpdateUserConfigRequest
from src.application.use_cases.user.get_user_config import GetUserConfigUseCase
from src.application.use_cases.user.update_user_config import UpdateUserConfigUseCase
from src.infrastructure.persistence.repositories.user_repository_impl import UserRepositoryImpl

class UserController:
    
    @staticmethod
    def get_config(user_id: int, db: Session) -> dict:
        user_repo = UserRepositoryImpl(db)
        use_case = GetUserConfigUseCase(user_repo)
        return use_case.execute(user_id)
    
    @staticmethod
    def update_config(user_id: int, request: UpdateUserConfigRequest, db: Session) -> dict:
        user_repo = UserRepositoryImpl(db)
        use_case = UpdateUserConfigUseCase(user_repo)
        return use_case.execute(user_id, request.settings)