from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict

@dataclass
class MinuteSummary:
    summary_id: str
    session_id: str
    activity_uuid: str
    minute_number: int
    timestamp: str
    
    predominant_emotion: str
    emotion_confidence_avg: float
    
    ear_avg: float
    pitch_avg: float
    yaw_avg: float
    
    looking_screen_percentage: float
    face_detected_percentage: float
    
    distraction_count: int
    drowsiness_count: int
    abrupt_changes_count: int
    
    cognitive_state: str
    engagement_level: str
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "summary_id": self.summary_id,
            "session_id": self.session_id,
            "activity_uuid": self.activity_uuid,
            "minute_number": self.minute_number,
            "timestamp": self.timestamp,
            "predominant_emotion": self.predominant_emotion,
            "emotion_confidence_avg": self.emotion_confidence_avg,
            "ear_avg": self.ear_avg,
            "pitch_avg": self.pitch_avg,
            "yaw_avg": self.yaw_avg,
            "looking_screen_percentage": self.looking_screen_percentage,
            "face_detected_percentage": self.face_detected_percentage,
            "distraction_count": self.distraction_count,
            "drowsiness_count": self.drowsiness_count,
            "abrupt_changes_count": self.abrupt_changes_count,
            "cognitive_state": self.cognitive_state,
            "engagement_level": self.engagement_level,
            "created_at": self.created_at
        }