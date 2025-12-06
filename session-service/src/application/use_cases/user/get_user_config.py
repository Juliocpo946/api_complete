from src.domain.repositories.user_repository import UserRepository

class GetUserConfigUseCase:
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def execute(self, user_id: int) -> dict:
        user = self.user_repo.get_by_id(user_id)
        print(f"\n[USE_CASE] Configuración obtenida para usuario: {user_id}\n")
        return user.to_dict()