from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

@dataclass
class UserActivity:
    activity_uuid: str
    session_id: str
    external_activity_id: int
    status: str = "in_progress"
    pause_count: int = 0
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    
    def complete(self):
        self.status = "completed"
        self.completed_at = datetime.now().isoformat()
    
    def abandon(self):
        self.status = "abandoned"
    
    def pause(self):
        self.status = "paused"
        self.pause_count += 1
    
    def resume(self):
        self.status = "in_progress"
    
    def to_dict(self) -> Dict:
        return {
            "activity_uuid": self.activity_uuid,
            "session_id": self.session_id,
            "external_activity_id": self.external_activity_id,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "pause_count": self.pause_count
        }