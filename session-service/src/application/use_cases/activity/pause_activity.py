from src.domain.repositories.activity_repository import ActivityRepository
from src.application.services.pause_tracker_service import PauseTrackerService

class PauseActivityUseCase:
    
    def __init__(self, activity_repo: ActivityRepository):
        self.activity_repo = activity_repo
    
    def execute(self, activity_uuid: str) -> dict:
        activity = self.activity_repo.get_by_uuid(activity_uuid)
        if not activity:
            return {"error": "Actividad no encontrada"}
        
        activity.pause()
        self.activity_repo.update(activity)
        PauseTrackerService.track_pause(activity_uuid)
        
        pause_count = PauseTrackerService.get_pause_count(activity_uuid)
        print(f"\n[USE_CASE] Actividad pausada: {activity_uuid}\n")
        return {"status": "paused", "pause_count": pause_count}