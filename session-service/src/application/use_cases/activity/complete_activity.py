from typing import Dict, Any
from src.domain.repositories.activity_repository import ActivityRepository
from src.domain.repositories.pause_counter_repository import PauseCounterRepository

class CompleteActivityUseCase:
    
    def __init__(self, activity_repo: ActivityRepository, pause_counter_repo: PauseCounterRepository):
        self.activity_repo = activity_repo
        self.pause_counter_repo = pause_counter_repo
    
    def execute(self, activity_uuid: str, feedback: Dict[str, Any]) -> dict:
        activity = self.activity_repo.get_by_uuid(activity_uuid)
        if not activity:
            return {"error": "Actividad no encontrada"}
        
        pause_counter = self.pause_counter_repo.get_by_activity(activity_uuid)
        pause_count = pause_counter.get_count() if pause_counter else 0
        
        activity.complete()
        self.activity_repo.update(activity)
        
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
