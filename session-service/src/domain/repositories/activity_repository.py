from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.activity import Activity

class ActivityRepository(ABC):
    
    @abstractmethod
    def create(self, activity: Activity) -> Activity:
        pass
    
    @abstractmethod
    def get_by_uuid(self, activity_uuid: str) -> Optional[Activity]:
        pass
    
    @abstractmethod
    def get_by_external_id(self, session_id: str, external_id: int) -> Optional[Activity]:
        pass
    
    @abstractmethod
    def update(self, activity: Activity) -> Activity:
        pass