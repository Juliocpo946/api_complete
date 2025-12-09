from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.entities.minute_summary import MinuteSummary

class MinuteSummaryRepository(ABC):
    
    @abstractmethod
    def save(self, summary: MinuteSummary) -> MinuteSummary:
        pass
    
    @abstractmethod
    def get_by_id(self, summary_id: str) -> Optional[MinuteSummary]:
        pass
    
    @abstractmethod
    def get_by_activity(self, activity_uuid: str) -> List[MinuteSummary]:
        pass