from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Emotion:
    name: str
    confidence: float
    cognitive_state: str

@dataclass
class EmotionBreakdown:
    emotion: str
    confidence: float

@dataclass
class SentimentAnalysis:
    primary_emotion: Emotion
    emotion_breakdown: List[EmotionBreakdown]
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            "primary_emotion": {
                "name": self.primary_emotion.name,
                "confidence": self.primary_emotion.confidence,
                "cognitive_state": self.primary_emotion.cognitive_state
            },
            "emotion_breakdown": [
                {"emotion": e.emotion, "confidence": e.confidence}
                for e in self.emotion_breakdown
            ],
            "timestamp": self.timestamp
        }