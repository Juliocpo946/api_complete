from typing import Dict
from src.domain.repositories.user_repository import UserRepository

class UpdateUserConfigUseCase:
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def execute(self, user_id: int, settings: Dict[str, bool]) -> dict:
        user = self.user_repo.get_by_id(user_id)
        user.update_settings(settings)
        self.user_repo.save(user)
        print(f"\n[USE_CASE] Configuración actualizada para usuario: {user_id}\n")
        print(f"Settings: {settings}\n")
        return user.to_dict()