from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict

@dataclass
class Session:
    session_id: str
    user_id: int
    disability_type: str
    cognitive_analysis_enabled: bool
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def pause(self):
        self.status = "paused"
    
    def resume(self):
        self.status = "active"
    
    def finalize(self):
        self.status = "finalized"
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "disability_type": self.disability_type,
            "cognitive_analysis_enabled": self.cognitive_analysis_enabled,
            "status": self.status,
            "created_at": self.created_at
        }