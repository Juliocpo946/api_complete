from src.domain.repositories.activity_repository import ActivityRepository
from src.application.services.pause_tracker_service import PauseTrackerService

class AbandonActivityUseCase:
    
    def __init__(self, activity_repo: ActivityRepository):
        self.activity_repo = activity_repo
    
    def execute(self, activity_uuid: str) -> dict:
        activity = self.activity_repo.get_by_uuid(activity_uuid)
        if not activity:
            return {"error": "Actividad no encontrada"}
        
        pause_count = PauseTrackerService.get_pause_count(activity_uuid)
        activity.abandon()
        self.activity_repo.update(activity)
        
        print(f"\n{'='*60}")
        print(f"[USE_CASE] Actividad abandonada")
        print(f"{'='*60}")
        print(f"Activity UUID: {activity_uuid}")
        print(f"Total de Pausas: {pause_count}")
        print(f"{'='*60}\n")
        
        PauseTrackerService.reset_counter(activity_uuid)
        return {"status": "abandoned", "pause_count": pause_count}

