from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ActivityMaster:
    external_activity_id: int
    title: str
    activity_type: str
    subtitle: Optional[str] = None
    content: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "external_activity_id": self.external_activity_id,
            "title": self.title,
            "subtitle": self.subtitle,
            "content": self.content,
            "activity_type": self.activity_type
        }