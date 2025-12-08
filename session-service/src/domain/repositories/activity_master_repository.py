from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.activity_master import ActivityMaster

class ActivityMasterRepository(ABC):
    
    @abstractmethod
    def create_or_update(self, activity_master: ActivityMaster) -> ActivityMaster:
        pass
    
    @abstractmethod
    def get_by_id(self, external_activity_id: int) -> Optional[ActivityMaster]:
        pass