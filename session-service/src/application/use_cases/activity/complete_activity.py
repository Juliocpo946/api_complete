from typing import Dict, Any
from src.domain.repositories.user_activity_repository import UserActivityRepository
from src.domain.repositories.pause_counter_repository import PauseCounterRepository

class CompleteActivityUseCase:
    
    def __init__(self, user_activity_repo: UserActivityRepository, pause_counter_repo: PauseCounterRepository):
        self.user_activity_repo = user_activity_repo
        self.pause_counter_repo = pause_counter_repo
    
    def execute(self, activity_uuid: str, feedback: Dict[str, Any]) -> dict:
        user_activity = self.user_activity_repo.get_by_uuid(activity_uuid)
        if not user_activity:
            return {"error": "Actividad no encontrada"}
        
        if user_activity.status == "completed":
            return {"error": "La actividad ya está completada"}
        
        if user_activity.status == "abandoned":
            return {"error": "No se puede completar una actividad abandonada"}
        
        pause_counter = self.pause_counter_repo.get_by_activity(activity_uuid)
        pause_count = pause_counter.get_count() if pause_counter else 0
        
        user_activity.complete()
        self.user_activity_repo.update(user_activity)
        
        if pause_counter:
            self.pause_counter_repo.delete(activity_uuid)
        
        print(f"\n{'='*60}")
        print(f"[USE_CASE] Actividad completada")
        print(f"{'='*60}")
        print(f"Activity UUID: {activity_uuid}")
        print(f"Total de Pausas: {pause_count}")
        print(f"Feedback: {feedback}")
        print(f"{'='*60}\n")
        
        return {"status": "completed", "pause_count": pause_count}