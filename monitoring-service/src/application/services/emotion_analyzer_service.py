from datetime import datetime
from typing import Dict, Optional
from collections import Counter
from src.domain.entities.emotion_state import EmotionState, FrameData
from src.domain.entities.minute_summary import MinuteSummary
from src.domain.entities.intervention import Intervention

emotion_states: Dict[str, EmotionState] = {}

class EmotionAnalyzerService:
    
    @staticmethod
    def initialize_activity(activity_uuid: str, session_id: str):
        emotion_states[activity_uuid] = EmotionState(
            activity_uuid=activity_uuid,
            session_id=session_id
        )
        print(f"\n[EMOTION ANALYZER] Actividad inicializada: {activity_uuid}")
    
    @staticmethod
    def pause_activity(activity_uuid: str):
        if activity_uuid in emotion_states:
            emotion_states[activity_uuid].is_paused = True
            print(f"\n[EMOTION ANALYZER] Análisis pausado: {activity_uuid}")
    
    @staticmethod
    def resume_activity(activity_uuid: str):
        if activity_uuid in emotion_states:
            state = emotion_states[activity_uuid]
            state.is_paused = False
            for key in state.last_intervention_time:
                state.last_intervention_time[key] = None
            print(f"\n[EMOTION ANALYZER] Análisis reanudado: {activity_uuid}")
    
    @staticmethod
    def finalize_activity(activity_uuid: str):
        if activity_uuid in emotion_states:
            del emotion_states[activity_uuid]
            print(f"\n[EMOTION ANALYZER] Actividad finalizada: {activity_uuid}")
    
    @staticmethod
    def process_frame(activity_uuid: str, frame_data: Dict) -> Optional[Intervention]:
        if activity_uuid not in emotion_states:
            return None
        
        state = emotion_states[activity_uuid]
        
        if state.is_paused:
            return None
        
        analisis = frame_data.get("analisis_sentimiento", {})
        biometricos = frame_data.get("datos_biometricos", {})
        emocion = analisis.get("emocion_principal", {})
        atencion = biometricos.get("atencion", {})
        somnolencia = biometricos.get("somnolencia", {})
        orientacion = atencion.get("orientacion_cabeza", {})
        
        frame = FrameData(
            timestamp=datetime.now(),
            emotion=emocion.get("nombre", "N/A"),
            confidence=emocion.get("confianza", 0.0),
            ear=somnolencia.get("apertura_ojos_ear", 0.0),
            pitch=orientacion.get("pitch", 0.0),
            yaw=orientacion.get("yaw", 0.0),
            looking_screen=atencion.get("mirando_pantalla", False),
            face_detected=biometricos.get("rostro_detectado", False),
            cognitive_state=emocion.get("estado_cognitivo", "unknown")
        )
        
        state.add_frame(frame)
        
        intervention = EmotionAnalyzerService._analyze_and_intervene(state)
        
        return intervention
    
    @staticmethod
    def _analyze_and_intervene(state: EmotionState) -> Optional[Intervention]:
        if state.is_in_grace_period():
            grace_check = EmotionAnalyzerService._check_grace_period_exception(state)
            if grace_check:
                return grace_check
            return None
        
        EmotionAnalyzerService._detect_sustained_events(state)
        
        if state.get_elapsed_minutes() >= 40:
            if state.can_send_intervention("pause", 999):
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion", 
                    "Han pasado 40 minutos. Te sugerimos tomar un descanso.",
                    "activity_duration"
                )
        
        if state.count_total_interventions_in_window(10) >= 3:
            if state.can_send_intervention("pause", 999):
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion",
                    "Has recibido múltiples intervenciones. Te sugerimos tomar un descanso.",
                    "intervention_limit"
                )
        
        frustration_intervention = EmotionAnalyzerService._check_frustration(state)
        if frustration_intervention:
            return frustration_intervention
        
        distraction_intervention = EmotionAnalyzerService._check_distraction(state)
        if distraction_intervention:
            return distraction_intervention
        
        drowsiness_intervention = EmotionAnalyzerService._check_drowsiness(state)
        if drowsiness_intervention:
            return drowsiness_intervention
        
        return None
    
    @staticmethod
    def _check_grace_period_exception(state: EmotionState) -> Optional[Intervention]:
        if len(state.frames) < 150:
            return None
        
        no_face_count = sum(1 for f in state.frames if not f.face_detected)
        if no_face_count == len(state.frames):
            if state.can_send_intervention("vibration", 999):
                state.record_intervention("vibration")
                return EmotionAnalyzerService._create_intervention(
                    state, "vibration_only",
                    None,
                    "camera_setup"
                )
        return None
    
    @staticmethod
    def _detect_sustained_events(state: EmotionState):
        if len(state.frames) < 15:
            return
        
        recent_frames = list(state.frames)[-15:]
        
        not_looking_consecutive = 0
        for frame in recent_frames:
            if not frame.looking_screen and frame.face_detected:
                not_looking_consecutive += 1
            else:
                if not_looking_consecutive >= 15:
                    state.add_distraction_event()
                not_looking_consecutive = 0
        
        low_ear_consecutive = 0
        for frame in recent_frames:
            if frame.ear < 0.25 and frame.face_detected:
                low_ear_consecutive += 1
            else:
                if low_ear_consecutive >= 25:
                    state.add_drowsiness_event()
                low_ear_consecutive = 0
        
        angry_consecutive = 0
        angry_sum = 0.0
        for frame in list(state.frames)[-100:]:
            if frame.emotion == "Angry" and frame.confidence > 0.75:
                angry_consecutive += 1
                angry_sum += frame.confidence
            else:
                angry_consecutive = 0
                angry_sum = 0.0
        
        if angry_consecutive >= 100:
            if state.frustration_start is None:
                state.frustration_start = datetime.now()
        else:
            state.frustration_start = None
    
    @staticmethod
    def _check_frustration(state: EmotionState) -> Optional[Intervention]:
        if state.frustration_start is None:
            return None
        
        frustration_duration = (datetime.now() - state.frustration_start).total_seconds()
        if frustration_duration < 20:
            return None
        
        recent_frames = list(state.frames)[-50:]
        angry_avg = sum(f.confidence for f in recent_frames if f.emotion == "Angry") / max(1, len(recent_frames))
        
        if angry_avg > 0.90:
            if state.can_send_intervention("pause", 999):
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion",
                    "Detectamos alta frustración. Te sugerimos tomar un descanso.",
                    "extreme_frustration"
                )
        
        if state.intervention_count["video"] + state.intervention_count["text"] >= 2:
            if state.can_send_intervention("pause", 999):
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion",
                    "Has recibido ayuda pero continúas frustrado. Te sugerimos un descanso.",
                    "persistent_frustration"
                )
        
        distraction_count_recent = state.count_recent_distractions(3)
        if distraction_count_recent >= 4:
            if state.can_send_intervention("video", 5):
                state.record_intervention("video")
                return EmotionAnalyzerService._create_intervention(
                    state, "video_instruction",
                    "Parece que tienes dificultades. Aquí hay un video de ayuda.",
                    "frustration_with_distraction",
                    video_url="https://res.cloudinary.com/doeofn1nd/video/upload/v1752085607/samples/elephants.mp4"
                )
        
        if angry_avg > 0.85:
            if state.can_send_intervention("video", 5):
                state.record_intervention("video")
                return EmotionAnalyzerService._create_intervention(
                    state, "video_instruction",
                    "Detectamos frustración. Te compartimos un video instructivo.",
                    "high_frustration",
                    video_url="https://res.cloudinary.com/doeofn1nd/video/upload/v1752085607/samples/elephants.mp4",
                    vibration=True
                )
        
        if state.intervention_count["video"] == 0:
            if state.can_send_intervention("video", 5):
                state.record_intervention("video")
                return EmotionAnalyzerService._create_intervention(
                    state, "video_instruction",
                    "Aquí tienes un video que puede ayudarte.",
                    "frustration",
                    video_url="https://res.cloudinary.com/doeofn1nd/video/upload/v1752085607/samples/elephants.mp4"
                )
        elif state.intervention_count["text"] == 0:
            if state.can_send_intervention("text", 5):
                state.record_intervention("text")
                return EmotionAnalyzerService._create_intervention(
                    state, "text_instruction",
                    "Recuerda seguir las instrucciones paso a paso. No te rindas.",
                    "frustration"
                )
        
        return None
    
    @staticmethod
    def _check_distraction(state: EmotionState) -> Optional[Intervention]:
        distraction_count_2min = state.count_recent_distractions(2)
        distraction_count_3min = state.count_recent_distractions(3)
        
        if distraction_count_3min >= 5:
            if state.intervention_count["vibration"] >= 3:
                if state.can_send_intervention("pause", 999):
                    state.record_intervention("pause")
                    return EmotionAnalyzerService._create_intervention(
                        state, "pause_suggestion",
                        "Detectamos distracciones frecuentes. Te sugerimos un descanso.",
                        "persistent_distraction"
                    )
        
        if distraction_count_2min >= 3:
            if state.can_send_intervention("vibration", 2):
                state.record_intervention("vibration")
                return EmotionAnalyzerService._create_intervention(
                    state, "vibration_only",
                    None,
                    "distraction"
                )
        
        return None
    
    @staticmethod
    def _check_drowsiness(state: EmotionState) -> Optional[Intervention]:
        drowsiness_count_2min = state.count_recent_drowsiness(2)
        
        if drowsiness_count_2min >= 3:
            if state.intervention_count["vibration"] >= 3:
                if state.can_send_intervention("pause", 999):
                    state.record_intervention("pause")
                    return EmotionAnalyzerService._create_intervention(
                        state, "pause_suggestion",
                        "Detectamos somnolencia persistente. Te sugerimos descansar.",
                        "persistent_drowsiness"
                    )
        
        if drowsiness_count_2min >= 2:
            if state.can_send_intervention("vibration", 2):
                state.record_intervention("vibration")
                return EmotionAnalyzerService._create_intervention(
                    state, "vibration_only",
                    None,
                    "drowsiness"
                )
        
        return None
    
    @staticmethod
    def _create_intervention(
        state: EmotionState,
        intervention_type: str,
        display_text: Optional[str],
        metric_name: str,
        video_url: Optional[str] = None,
        vibration: bool = False
    ) -> Intervention:
        packet_id = f"int_{datetime.now().timestamp()}"
        
        if intervention_type == "vibration_only":
            vibration = True
            display_text = None
            video_url = None
        
        return Intervention(
            packet_id=packet_id,
            session_id=state.session_id,
            activity_uuid=state.activity_uuid,
            intervention_type=intervention_type,
            video_url=video_url,
            display_text=display_text,
            vibration_enabled=vibration,
            metric_name=metric_name,
            metric_value=0.0,
            confidence=0.0,
            duration_ms=5000
        )
    
    @staticmethod
    def generate_minute_summary(activity_uuid: str) -> Optional[MinuteSummary]:
        if activity_uuid not in emotion_states:
            return None
        
        state = emotion_states[activity_uuid]
        
        if len(state.frames) == 0:
            return None
        
        minute_number = int(state.get_elapsed_minutes())
        
        recent_frames = list(state.frames)
        
        emotions = [f.emotion for f in recent_frames if f.emotion != "N/A"]
        if not emotions:
            predominant_emotion = "N/A"
            emotion_confidence_avg = 0.0
        else:
            emotion_counter = Counter(emotions)
            predominant_emotion = emotion_counter.most_common(1)[0][0]
            emotion_frames = [f for f in recent_frames if f.emotion == predominant_emotion]
            emotion_confidence_avg = sum(f.confidence for f in emotion_frames) / len(emotion_frames)
        
        ear_values = [f.ear for f in recent_frames if f.ear > 0]
        ear_avg = sum(ear_values) / len(ear_values) if ear_values else 0.0
        
        pitch_values = [f.pitch for f in recent_frames if f.pitch != 0]
        pitch_avg = sum(pitch_values) / len(pitch_values) if pitch_values else 0.0
        
        yaw_values = [f.yaw for f in recent_frames if f.yaw != 0]
        yaw_avg = sum(yaw_values) / len(yaw_values) if yaw_values else 0.0
        
        looking_count = sum(1 for f in recent_frames if f.looking_screen)
        looking_screen_percentage = (looking_count / len(recent_frames)) * 100
        
        face_count = sum(1 for f in recent_frames if f.face_detected)
        face_detected_percentage = (face_count / len(recent_frames)) * 100
        
        distraction_count = state.count_recent_distractions(1)
        drowsiness_count = state.count_recent_drowsiness(1)
        
        cognitive_states = [f.cognitive_state for f in recent_frames if f.cognitive_state != "unknown"]
        if cognitive_states:
            cognitive_counter = Counter(cognitive_states)
            cognitive_state = cognitive_counter.most_common(1)[0][0]
        else:
            cognitive_state = "unknown"
        
        if looking_screen_percentage > 80 and emotion_confidence_avg > 0.6:
            engagement_level = "high"
        elif looking_screen_percentage > 50:
            engagement_level = "medium"
        else:
            engagement_level = "low"
        
        summary_id = f"sum_{state.activity_uuid}_{minute_number}"
        
        return MinuteSummary(
            summary_id=summary_id,
            session_id=state.session_id,
            activity_uuid=state.activity_uuid,
            minute_number=minute_number,
            timestamp=datetime.now().isoformat(),
            predominant_emotion=predominant_emotion,
            emotion_confidence_avg=emotion_confidence_avg,
            ear_avg=ear_avg,
            pitch_avg=pitch_avg,
            yaw_avg=yaw_avg,
            looking_screen_percentage=looking_screen_percentage,
            face_detected_percentage=face_detected_percentage,
            distraction_count=distraction_count,
            drowsiness_count=drowsiness_count,
            abrupt_changes_count=0,
            cognitive_state=cognitive_state,
            engagement_level=engagement_level
        )