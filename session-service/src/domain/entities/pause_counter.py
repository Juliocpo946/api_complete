from dataclasses import dataclass, field
from typing import Dict

@dataclass
class PauseCounter:
    activity_uuid: str
    count: int = 0
    paused_timestamps: list = field(default_factory=list)
    
    def increment(self, timestamp: str):
        self.count += 1
        self.paused_timestamps.append(timestamp)
    
    def get_count(self) -> int:
        return self.count
    
    def to_dict(self) -> Dict:
        return {
            "activity_uuid": self.activity_uuid,
            "pause_count": self.count,
            "timestamps": self.paused_timestamps
        }