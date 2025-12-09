from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque

@dataclass
class FrameData:
    timestamp: datetime
    emotion: str
    confidence: float
    ear: float
    pitch: float
    yaw: float
    looking_screen: bool
    face_detected: bool
    cognitive_state: str

@dataclass
class EmotionState:
    activity_uuid: str
    session_id: str
    activity_start_time: datetime = field(default_factory=datetime.now)
    frames: deque = field(default_factory=lambda: deque(maxlen=300))
    
    intervention_count: Dict[str, int] = field(default_factory=lambda: {
        "video": 0,
        "text": 0,
        "vibration": 0,
        "pause": 0
    })
    
    last_intervention_time: Dict[str, Optional[datetime]] = field(default_factory=lambda: {
        "video": None,
        "text": None,
        "vibration": None,
        "pause": None
    })
    
    distraction_events: List[datetime] = field(default_factory=list)
    drowsiness_events: List[datetime] = field(default_factory=list)
    frustration_start: Optional[datetime] = None
    
    last_minute_summary: Optional[datetime] = None
    is_paused: bool = False
    
    def add_frame(self, frame: FrameData):
        self.frames.append(frame)
    
    def get_elapsed_minutes(self) -> float:
        return (datetime.now() - self.activity_start_time).total_seconds() / 60
    
    def is_in_grace_period(self) -> bool:
        return self.get_elapsed_minutes() < 3
    
    def can_send_intervention(self, intervention_type: str, cooldown_minutes: int) -> bool:
        last_time = self.last_intervention_time.get(intervention_type)
        if last_time is None:
            return True
        elapsed = (datetime.now() - last_time).total_seconds() / 60
        return elapsed >= cooldown_minutes
    
    def record_intervention(self, intervention_type: str):
        self.intervention_count[intervention_type] += 1
        self.last_intervention_time[intervention_type] = datetime.now()
    
    def add_distraction_event(self):
        self.distraction_events.append(datetime.now())
        self._clean_old_events(self.distraction_events, minutes=10)
    
    def add_drowsiness_event(self):
        self.drowsiness_events.append(datetime.now())
        self._clean_old_events(self.drowsiness_events, minutes=10)
    
    def _clean_old_events(self, event_list: List[datetime], minutes: int):
        cutoff = datetime.now().timestamp() - (minutes * 60)
        while event_list and event_list[0].timestamp() < cutoff:
            event_list.pop(0)
    
    def count_recent_distractions(self, minutes: int) -> int:
        cutoff = datetime.now().timestamp() - (minutes * 60)
        return sum(1 for event in self.distraction_events if event.timestamp() >= cutoff)
    
    def count_recent_drowsiness(self, minutes: int) -> int:
        cutoff = datetime.now().timestamp() - (minutes * 60)
        return sum(1 for event in self.drowsiness_events if event.timestamp() >= cutoff)
    
    def count_total_interventions_in_window(self, minutes: int) -> int:
        cutoff = datetime.now().timestamp() - (minutes * 60)
        count = 0
        for intervention_type, last_time in self.last_intervention_time.items():
            if last_time and last_time.timestamp() >= cutoff:
                count += 1
        return count