from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.user_activity import UserActivity

class UserActivityRepository(ABC):
    
    @abstractmethod
    def create(self, user_activity: UserActivity) -> UserActivity:
        pass
    
    @abstractmethod
    def get_by_uuid(self, activity_uuid: str) -> Optional[UserActivity]:
        pass
    
    @abstractmethod
    def get_by_external_id(self, session_id: str, external_id: int) -> Optional[UserActivity]:
        pass
    
    @abstractmethod
    def update(self, user_activity: UserActivity) -> UserActivity:
        pass