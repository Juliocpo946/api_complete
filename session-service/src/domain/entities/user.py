from typing import Dict
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    user_id: int
    settings: Dict[str, bool] = field(default_factory=dict)
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        if not self.settings:
            self.settings = {
                "cognitive_analysis_enabled": True,
                "text_notifications": True,
                "video_suggestions": True,
                "vibration_alerts": True,
                "pause_suggestions": False
            }
    
    def update_settings(self, new_settings: Dict[str, bool]):
        self.settings.update(new_settings)
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "updated_at": self.updated_at,
            "settings": self.settings
        }