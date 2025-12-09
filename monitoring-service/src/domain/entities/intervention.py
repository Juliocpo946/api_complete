from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime

@dataclass
class Intervention:
    packet_id: str
    session_id: str
    activity_uuid: str
    intervention_type: str
    video_url: Optional[str] = None
    display_text: Optional[str] = None
    vibration_enabled: bool = False
    metric_name: str = ""
    metric_value: float = 0.0
    confidence: float = 0.0
    duration_ms: int = 5000
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "packet_id": self.packet_id,
            "timestamp": self.timestamp,
            "type": "intervention",
            "triggers": {
                "video_url": self.video_url,
                "display_text": self.display_text,
                "vibration_enabled": self.vibration_enabled
            },
            "details": {
                "metric_name": self.metric_name,
                "value": self.metric_value,
                "confidence": self.confidence,
                "duration_ms": self.duration_ms
            }
        }