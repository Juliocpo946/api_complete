from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.pause_counter import PauseCounter

class PauseCounterRepository(ABC):
    
    @abstractmethod
    def create(self, pause_counter: PauseCounter) -> PauseCounter:
        pass
    
    @abstractmethod
    def get_by_activity(self, activity_uuid: str) -> Optional[PauseCounter]:
        pass
    
    @abstractmethod
    def update(self, pause_counter: PauseCounter) -> PauseCounter:
        pass
    
    @abstractmethod
    def increment(self, activity_uuid: str, timestamp: str) -> PauseCounter:
        pass
    
    @abstractmethod
    def delete(self, activity_uuid: str) -> bool:
        pass