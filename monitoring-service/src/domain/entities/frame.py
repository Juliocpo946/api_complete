from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime

@dataclass
class Frame:
    frame_id: str
    session_id: str
    activity_uuid: str
    timestamp: str
    sentiment_analysis: Dict[str, Any] = field(default_factory=dict)
    biometric_data: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "frame_id": self.frame_id,
            "session_id": self.session_id,
            "activity_uuid": self.activity_uuid,
            "timestamp": self.timestamp,
            "sentiment_analysis": self.sentiment_analysis,
            "biometric_data": self.biometric_data,
            "created_at": self.created_at
        }