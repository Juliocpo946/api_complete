from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.frame import Frame

class FrameRepository(ABC):
    
    @abstractmethod
    def save(self, frame: Frame) -> Frame:
        pass
    
    @abstractmethod
    def get_by_id(self, frame_id: str) -> Optional[Frame]:
        pass
    
    @abstractmethod
    def get_by_activity(self, activity_uuid: str) -> List[Frame]:
        pass