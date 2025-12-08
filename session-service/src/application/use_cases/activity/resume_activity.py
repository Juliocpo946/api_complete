from src.domain.repositories.user_activity_repository import UserActivityRepository
from src.application.services.pause_tracker_service import PauseTrackerService

class ResumeActivityUseCase:
    
    def __init__(self, user_activity_repo: UserActivityRepository):
        self.user_activity_repo = user_activity_repo
    
    def execute(self, activity_uuid: str) -> dict:
        user_activity = self.user_activity_repo.get_by_uuid(activity_uuid)
        if not user_activity:
            return {"error": "Actividad no encontrada"}
        
        user_activity.resume()
        self.user_activity_repo.update(user_activity)
        
        pause_count = PauseTrackerService.get_pause_count(activity_uuid)
        print(f"\n[USE_CASE] Actividad reanudada: {activity_uuid}\n")
        return {"status": "in_progress", "pause_count": pause_count}