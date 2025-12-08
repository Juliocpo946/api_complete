from datetime import datetime
from src.domain.repositories.user_activity_repository import UserActivityRepository
from src.domain.repositories.pause_counter_repository import PauseCounterRepository

class PauseActivityUseCase:
    
    def __init__(self, user_activity_repo: UserActivityRepository, pause_counter_repo: PauseCounterRepository):
        self.user_activity_repo = user_activity_repo
        self.pause_counter_repo = pause_counter_repo
    
    def execute(self, activity_uuid: str) -> dict:
        user_activity = self.user_activity_repo.get_by_uuid(activity_uuid)
        if not user_activity:
            return {"error": "Actividad no encontrada"}
        
        user_activity.pause()
        self.user_activity_repo.update(user_activity)
        
        pause_counter = self.pause_counter_repo.increment(
            activity_uuid,
            datetime.now().isoformat()
        )
        
        pause_count = pause_counter.get_count()
        print(f"\n[USE_CASE] Actividad pausada: {activity_uuid}\n")
        print(f"Total de pausas registradas en BD: {pause_count}\n")
        return {"status": "paused", "pause_count": pause_count}