from datetime import datetime
from typing import Dict, Optional
from collections import Counter
from src.domain.entities.emotion_state import EmotionState, FrameData
from src.domain.entities.minute_summary import MinuteSummary
from src.domain.entities.intervention import Intervention

emotion_states: Dict[str, EmotionState] = {}

class EmotionAnalyzerService:
    @staticmethod
    def initialize_activity(activity_uuid: str, session_id: str, user_id: int = None, user_cluster: str = None):
        emotion_states[activity_uuid] = EmotionState(
            activity_uuid=activity_uuid,
            session_id=session_id,
            user_id=user_id,
            user_cluster=user_cluster
        )
        print(f"\n[EMOTION ANALYZER] Actividad inicializada: {activity_uuid}")
        if user_cluster:
            print(f"[EMOTION ANALYZER] Cluster detectado: {user_cluster}")
    
    @staticmethod
    def _analyze_and_intervene(state: EmotionState) -> Optional[Intervention]:
        thresholds = state.get_thresholds()
        
        last_any_intervention = max(
            (t for t in state.last_intervention_time.values() if t is not None),
            default=None
        )
        if last_any_intervention:
            seconds_since_last = (datetime.now() - last_any_intervention).total_seconds()
            if seconds_since_last < 180:
                return None
        
        if state.is_in_grace_period():
            grace_check = EmotionAnalyzerService._check_grace_period_exception(state)
            if grace_check:
                return grace_check
            return None
        
        EmotionAnalyzerService._detect_sustained_events(state)
        
        if state.get_elapsed_minutes() >= thresholds['pause_time_minutes']:
            if state.can_send_intervention("pause", 10):
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion", 
                    f"Han pasado {int(thresholds['pause_time_minutes'])} minutos. Te sugerimos tomar un descanso.",
                    "activity_duration",
                    metric_value=state.get_elapsed_minutes(),
                    confidence=1.0
                )
        
        if state.count_total_interventions_in_window(10) >= 3:
            if state.can_send_intervention("pause", 10):
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion",
                    "Has recibido múltiples intervenciones. Te sugerimos tomar un descanso.",
                    "intervention_limit",
                    metric_value=state.count_total_interventions_in_window(10),
                    confidence=0.95
                )
        
        frustration_intervention = EmotionAnalyzerService._check_frustration(state, thresholds)
        if frustration_intervention:
            return frustration_intervention
        
        distraction_intervention = EmotionAnalyzerService._check_distraction(state, thresholds)
        if distraction_intervention:
            return distraction_intervention
        
        drowsiness_intervention = EmotionAnalyzerService._check_drowsiness(state, thresholds)
        if drowsiness_intervention:
            return drowsiness_intervention
        
        return None
    
    @staticmethod
    def _check_frustration(state: EmotionState, thresholds: Dict[str, float]) -> Optional[Intervention]:
        if state.frustration_start is None:
            return None
        
        frustration_duration = (datetime.now() - state.frustration_start).total_seconds()
        if frustration_duration < 20:
            return None
        
        recent_frames = list(state.frames)[-50:]
        angry_frames = [f for f in recent_frames if f.emotion == "Angry"]
        angry_avg = sum(f.confidence for f in angry_frames) / max(1, len(recent_frames))
        angry_confidence = sum(f.confidence for f in angry_frames) / max(1, len(angry_frames)) if angry_frames else 0.0
        
        frustration_threshold = thresholds['frustration_threshold']
        
        if angry_avg > frustration_threshold:
            if state.can_send_intervention("pause", 10):
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion",
                    "Detectamos alta frustración. Te sugerimos tomar un descanso.",
                    "extreme_frustration",
                    metric_value=angry_avg,
                    confidence=angry_confidence
                )
        
        elif state.intervention_count["video"] + state.intervention_count["text"] >= 2:
            if state.can_send_intervention("pause", 10):
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion",
                    "Has recibido ayuda pero continúas frustrado. Te sugerimos un descanso.",
                    "persistent_frustration",
                    metric_value=angry_avg,
                    confidence=angry_confidence
                )
        
        elif state.count_recent_distractions(3) >= 4:
            if state.can_send_intervention("video", 5):
                state.record_intervention("video")
                return EmotionAnalyzerService._create_intervention(
                    state, "video_instruction",
                    "Parece que tienes dificultades. Aquí hay un video de ayuda.",
                    "frustration_with_distraction",
                    video_url="https://res.cloudinary.com/doeofn1nd/video/upload/v1752085607/samples/elephants.mp4",
                    metric_value=angry_avg,
                    confidence=angry_confidence
                )
        
        elif angry_avg > (frustration_threshold - 0.05):
            if state.can_send_intervention("video", 5):
                state.record_intervention("video")
                return EmotionAnalyzerService._create_intervention(
                    state, "video_instruction",
                    "Detectamos frustración. Te compartimos un video instructivo.",
                    "high_frustration",
                    video_url="https://res.cloudinary.com/doeofn1nd/video/upload/v1752085607/samples/elephants.mp4",
                    vibration=True,
                    metric_value=angry_avg,
                    confidence=angry_confidence
                )
        
        elif state.intervention_count["video"] == 0:
            if state.can_send_intervention("video", 5):
                state.record_intervention("video")
                return EmotionAnalyzerService._create_intervention(
                    state, "video_instruction",
                    "Aquí tienes un video que puede ayudarte.",
                    "frustration",
                    video_url="https://res.cloudinary.com/doeofn1nd/video/upload/v1752085607/samples/elephants.mp4",
                    metric_value=angry_avg,
                    confidence=angry_confidence
                )
        
        elif state.intervention_count["text"] == 0:
            if state.can_send_intervention("text", 5):
                state.record_intervention("text")
                return EmotionAnalyzerService._create_intervention(
                    state, "text_instruction",
                    "Recuerda seguir las instrucciones paso a paso. No te rindas.",
                    "frustration",
                    metric_value=angry_avg,
                    confidence=angry_confidence
                )
        
        return None
    
    @staticmethod
    def _check_distraction(state: EmotionState, thresholds: Dict[str, float]) -> Optional[Intervention]:
        distraction_count_2min = state.count_recent_distractions(2)
        distraction_count_3min = state.count_recent_distractions(3)
        
        recent_frames = list(state.frames)[-60:]
        not_looking_count = sum(1 for f in recent_frames if not f.looking_screen and f.face_detected)
        distraction_metric = not_looking_count / max(1, len(recent_frames))
        
        distraction_threshold = thresholds['distraction_threshold']
        
        if distraction_count_3min >= 5 and state.intervention_count["vibration"] >= 3:
            if state.can_send_intervention("pause", 10):
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion",
                    "Detectamos distracciones frecuentes. Te sugerimos un descanso.",
                    "persistent_distraction",
                    metric_value=distraction_metric,
                    confidence=0.90
                )
        
        elif distraction_count_2min >= distraction_threshold:
            if state.can_send_intervention("vibration", 2):
                state.record_intervention("vibration")
                return EmotionAnalyzerService._create_intervention(
                    state, "vibration_only",
                    None,
                    "distraction",
                    metric_value=distraction_metric,
                    confidence=0.85
                )
        
        return None
    
    @staticmethod
    def _check_drowsiness(state: EmotionState, thresholds: Dict[str, float]) -> Optional[Intervention]:
        drowsiness_count_2min = state.count_recent_drowsiness(2)
        
        recent_frames = list(state.frames)[-60:]
        ear_values = [f.ear for f in recent_frames if f.ear > 0 and f.face_detected]
        avg_ear = sum(ear_values) / len(ear_values) if ear_values else 0.0
        drowsiness_metric = 1.0 - min(avg_ear / 0.3, 1.0)
        
        drowsiness_threshold = thresholds['drowsiness_threshold']
        
        if drowsiness_count_2min >= 3 and state.intervention_count["vibration"] >= 3:
            if state.can_send_intervention("pause", 10):
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion",
                    "Detectamos somnolencia persistente. Te sugerimos descansar.",
                    "persistent_drowsiness",
                    metric_value=drowsiness_metric,
                    confidence=0.90
                )
        
        elif drowsiness_count_2min >= drowsiness_threshold:
            if state.can_send_intervention("vibration", 2):
                state.record_intervention("vibration")
                return EmotionAnalyzerService._create_intervention(
                    state, "vibration_only",
                    None,
                    "drowsiness",
                    metric_value=drowsiness_metric,
                    confidence=0.85
                )
        
        return None