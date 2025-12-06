from datetime import datetime
from typing import Dict
from src.domain.entities.pause_counter import PauseCounter

pause_counters: Dict[str, PauseCounter] = {}

class PauseTrackerService:
    
    @staticmethod
    def track_pause(activity_uuid: str) -> PauseCounter:
        if activity_uuid not in pause_counters:
            pause_counters[activity_uuid] = PauseCounter(activity_uuid=activity_uuid)
        
        counter = pause_counters[activity_uuid]
        counter.increment(datetime.now().isoformat())
        
        print(f"\n{'='*60}")
        print(f"[PAUSE TRACKER]")
        print(f"{'='*60}")
        print(f"Actividad: {activity_uuid}")
        print(f"Contador de Pausas: {counter.get_count()}")
        print(f"Timestamps: {counter.paused_timestamps}")
        print(f"{'='*60}\n")
        
        return counter
    
    @staticmethod
    def get_pause_count(activity_uuid: str) -> int:
        if activity_uuid in pause_counters:
            return pause_counters[activity_uuid].get_count()
        return 0
    
    @staticmethod
    def reset_counter(activity_uuid: str):
        if activity_uuid in pause_counters:
            del pause_counters[activity_uuid]
            print(f"\n[PAUSE TRACKER] Contador reiniciado: {activity_uuid}\n")