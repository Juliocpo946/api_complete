from src.domain.repositories.activity_repository import ActivityRepository
from src.application.services.pause_tracker_service import PauseTrackerService

class ResumeActivityUseCase:
    
    def __init__(self, activity_repo: ActivityRepository):
        self.activity_repo = activity_repo
    
    def execute(self, activity_uuid: str) -> dict:
        activity = self.activity_repo.get_by_uuid(activity_uuid)
        if not activity:
            return {"error": "Actividad no encontrada"}
        
        activity.resume()
        self.activity_repo.update(activity)
        
        pause_count = PauseTrackerService.get_pause_count(activity_uuid)
        print(f"\n[USE_CASE] Actividad reanudada: {activity_uuid}\n")
        return {"status": "in_progress", "pause_count": pause_count}