from datetime import datetime
from src.domain.repositories.activity_repository import ActivityRepository
from src.domain.repositories.pause_counter_repository import PauseCounterRepository

class PauseActivityUseCase:
    
    def __init__(self, activity_repo: ActivityRepository, pause_counter_repo: PauseCounterRepository):
        self.activity_repo = activity_repo
        self.pause_counter_repo = pause_counter_repo
    
    def execute(self, activity_uuid: str) -> dict:
        activity = self.activity_repo.get_by_uuid(activity_uuid)
        if not activity:
            return {"error": "Actividad no encontrada"}
        
        activity.pause()
        self.activity_repo.update(activity)
        
        pause_counter = self.pause_counter_repo.increment(
            activity_uuid,
            datetime.now().isoformat()
        )
        
        pause_count = pause_counter.get_count()
        print(f"\n[USE_CASE] Actividad pausada: {activity_uuid}\n")
        print(f"Total de pausas registradas en BD: {pause_count}\n")
        return {"status": "paused", "pause_count": pause_count}