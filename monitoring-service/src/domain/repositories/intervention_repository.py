from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.intervention import Intervention

class InterventionRepository(ABC):
    
    @abstractmethod
    def save(self, intervention: Intervention) -> Intervention:
        pass
    
    @abstractmethod
    def get_by_id(self, packet_id: str) -> Optional[Intervention]:
        pass
    
    @abstractmethod
    def get_by_activity(self, activity_uuid: str) -> List[Intervention]:
        pass