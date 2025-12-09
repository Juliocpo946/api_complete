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
        # COOLDOWN GLOBAL: No enviar ninguna intervención si ya enviamos una hace menos de 3 minutos
        last_any_intervention = max(
            (t for t in state.last_intervention_time.values() if t is not None),
            default=None
        )
        if last_any_intervention:
            seconds_since_last = (datetime.now() - last_any_intervention).total_seconds()
            if seconds_since_last < 180:  # 3 minutos = 180 segundos
                return None
        
        # Periodo de gracia: solo verificar excepción crítica
        if state.is_in_grace_period():
            grace_check = EmotionAnalyzerService._check_grace_period_exception(state)
            if grace_check:
                return grace_check
            return None
        
        # Detectar eventos sostenidos (actualizar contadores internos)
        EmotionAnalyzerService._detect_sustained_events(state)
        
        # Verificar límite de tiempo (40 minutos)
        if state.get_elapsed_minutes() >= 40:
            if state.can_send_intervention("pause", 10):  # Cooldown de 10 minutos para pausas
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion", 
                    "Han pasado 40 minutos. Te sugerimos tomar un descanso.",
                    "activity_duration",
                    metric_value=state.get_elapsed_minutes(),
                    confidence=1.0
                )
        
        # Verificar límite de intervenciones (3 en 10 minutos)
        if state.count_total_interventions_in_window(10) >= 3:
            if state.can_send_intervention("pause", 10):  # Cooldown de 10 minutos para pausas
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion",
                    "Has recibido múltiples intervenciones. Te sugerimos tomar un descanso.",
                    "intervention_limit",
                    metric_value=state.count_total_interventions_in_window(10),
                    confidence=0.95
                )
        
        # PRIORIDAD 1: Frustración (video/texto de instrucciones o pausa si persiste)
        frustration_intervention = EmotionAnalyzerService._check_frustration(state)
        if frustration_intervention:
            return frustration_intervention
        
        # PRIORIDAD 2: Distracción (vibración o pausa si persiste)
        distraction_intervention = EmotionAnalyzerService._check_distraction(state)
        if distraction_intervention:
            return distraction_intervention
        
        # PRIORIDAD 3: Somnolencia (vibración o pausa si persiste)
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
            if state.can_send_intervention("vibration", 2):  # Cooldown de 2 minutos para vibraciones
                state.record_intervention("vibration")
                return EmotionAnalyzerService._create_intervention(
                    state, "vibration_only",
                    None,
                    "camera_setup",
                    metric_value=no_face_count / len(state.frames),
                    confidence=1.0
                )
        return None
    
    @staticmethod
    def _detect_sustained_events(state: EmotionState):
        if len(state.frames) < 15:
            return
        
        recent_frames = list(state.frames)[-15:]
        
        # Detectar distracción sostenida (15 frames seguidos sin mirar pantalla)
        not_looking_consecutive = 0
        for frame in recent_frames:
            if not frame.looking_screen and frame.face_detected:
                not_looking_consecutive += 1
            else:
                if not_looking_consecutive >= 15:
                    state.add_distraction_event()
                not_looking_consecutive = 0
        
        # Detectar somnolencia sostenida (25 frames seguidos con EAR bajo)
        low_ear_consecutive = 0
        for frame in recent_frames:
            if frame.ear < 0.25 and frame.face_detected:
                low_ear_consecutive += 1
            else:
                if low_ear_consecutive >= 25:
                    state.add_drowsiness_event()
                low_ear_consecutive = 0
        
        # Detectar frustración sostenida (100 frames seguidos de Angry)
        angry_consecutive = 0
        for frame in list(state.frames)[-100:]:
            if frame.emotion == "Angry" and frame.confidence > 0.75:
                angry_consecutive += 1
            else:
                angry_consecutive = 0
        
        if angry_consecutive >= 100:
            if state.frustration_start is None:
                state.frustration_start = datetime.now()
        else:
            state.frustration_start = None
    
    @staticmethod
    def _check_frustration(state: EmotionState) -> Optional[Intervention]:
        """
        Jerarquía de frustración:
        1. Frustración extrema (angry_avg > 0.90) → Pausa
        2. Frustración persistente después de ayuda → Pausa
        3. Frustración alta + distracción → Video
        4. Frustración alta → Video con vibración
        5. Frustración moderada sin ayuda previa → Video
        6. Frustración moderada con video previo → Texto
        """
        if state.frustration_start is None:
            return None
        
        frustration_duration = (datetime.now() - state.frustration_start).total_seconds()
        if frustration_duration < 20:
            return None
        
        recent_frames = list(state.frames)[-50:]
        angry_frames = [f for f in recent_frames if f.emotion == "Angry"]
        angry_avg = sum(f.confidence for f in angry_frames) / max(1, len(recent_frames))
        angry_confidence = sum(f.confidence for f in angry_frames) / max(1, len(angry_frames)) if angry_frames else 0.0
        
        # 1. FRUSTRACIÓN EXTREMA → Pausa inmediata
        if angry_avg > 0.90:
            if state.can_send_intervention("pause", 10):  # Cooldown de 10 minutos para pausas
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion",
                    "Detectamos alta frustración. Te sugerimos tomar un descanso.",
                    "extreme_frustration",
                    metric_value=angry_avg,
                    confidence=angry_confidence
                )
        
        # 2. FRUSTRACIÓN PERSISTENTE después de 2 ayudas → Pausa
        elif state.intervention_count["video"] + state.intervention_count["text"] >= 2:
            if state.can_send_intervention("pause", 10):  # Cooldown de 10 minutos para pausas
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion",
                    "Has recibido ayuda pero continúas frustrado. Te sugerimos un descanso.",
                    "persistent_frustration",
                    metric_value=angry_avg,
                    confidence=angry_confidence
                )
        
        # 3. FRUSTRACIÓN ALTA + DISTRACCIÓN → Video
        elif state.count_recent_distractions(3) >= 4:
            if state.can_send_intervention("video", 5):  # Cooldown de 5 minutos para videos
                state.record_intervention("video")
                return EmotionAnalyzerService._create_intervention(
                    state, "video_instruction",
                    "Parece que tienes dificultades. Aquí hay un video de ayuda.",
                    "frustration_with_distraction",
                    video_url="https://res.cloudinary.com/doeofn1nd/video/upload/v1752085607/samples/elephants.mp4",
                    metric_value=angry_avg,
                    confidence=angry_confidence
                )
        
        # 4. FRUSTRACIÓN ALTA → Video con vibración
        elif angry_avg > 0.85:
            if state.can_send_intervention("video", 5):  # Cooldown de 5 minutos para videos
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
        
        # 5. FRUSTRACIÓN MODERADA sin video previo → Video
        elif state.intervention_count["video"] == 0:
            if state.can_send_intervention("video", 5):  # Cooldown de 5 minutos para videos
                state.record_intervention("video")
                return EmotionAnalyzerService._create_intervention(
                    state, "video_instruction",
                    "Aquí tienes un video que puede ayudarte.",
                    "frustration",
                    video_url="https://res.cloudinary.com/doeofn1nd/video/upload/v1752085607/samples/elephants.mp4",
                    metric_value=angry_avg,
                    confidence=angry_confidence
                )
        
        # 6. FRUSTRACIÓN MODERADA con video previo → Texto
        elif state.intervention_count["text"] == 0:
            if state.can_send_intervention("text", 5):  # Cooldown de 5 minutos para textos
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
    def _check_distraction(state: EmotionState) -> Optional[Intervention]:
        """
        Jerarquía de distracción:
        1. Distracción persistente después de 3 vibraciones → Pausa
        2. Distracción frecuente (3+ eventos en 2 minutos) → Vibración
        """
        distraction_count_2min = state.count_recent_distractions(2)
        distraction_count_3min = state.count_recent_distractions(3)
        
        # Calcular métrica de distracción
        recent_frames = list(state.frames)[-60:]  # Últimos 60 frames (~2 segundos a 30fps)
        not_looking_count = sum(1 for f in recent_frames if not f.looking_screen and f.face_detected)
        distraction_metric = not_looking_count / max(1, len(recent_frames))
        
        # 1. DISTRACCIÓN PERSISTENTE después de 3 vibraciones → Pausa
        if distraction_count_3min >= 5 and state.intervention_count["vibration"] >= 3:
            if state.can_send_intervention("pause", 10):  # Cooldown de 10 minutos para pausas
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion",
                    "Detectamos distracciones frecuentes. Te sugerimos un descanso.",
                    "persistent_distraction",
                    metric_value=distraction_metric,
                    confidence=0.90
                )
        
        # 2. DISTRACCIÓN FRECUENTE → Vibración
        elif distraction_count_2min >= 3:
            if state.can_send_intervention("vibration", 2):  # Cooldown de 2 minutos para vibraciones
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
    def _check_drowsiness(state: EmotionState) -> Optional[Intervention]:
        """
        Jerarquía de somnolencia:
        1. Somnolencia persistente después de 3 vibraciones → Pausa
        2. Somnolencia frecuente (2+ eventos en 2 minutos) → Vibración
        """
        drowsiness_count_2min = state.count_recent_drowsiness(2)
        
        # Calcular métrica de somnolencia
        recent_frames = list(state.frames)[-60:]  # Últimos 60 frames
        ear_values = [f.ear for f in recent_frames if f.ear > 0 and f.face_detected]
        avg_ear = sum(ear_values) / len(ear_values) if ear_values else 0.0
        drowsiness_metric = 1.0 - min(avg_ear / 0.3, 1.0)  # Normalizado: EAR bajo = métrica alta
        
        # 1. SOMNOLENCIA PERSISTENTE después de 3 vibraciones → Pausa
        if drowsiness_count_2min >= 3 and state.intervention_count["vibration"] >= 3:
            if state.can_send_intervention("pause", 10):  # Cooldown de 10 minutos para pausas
                state.record_intervention("pause")
                return EmotionAnalyzerService._create_intervention(
                    state, "pause_suggestion",
                    "Detectamos somnolencia persistente. Te sugerimos descansar.",
                    "persistent_drowsiness",
                    metric_value=drowsiness_metric,
                    confidence=0.90
                )
        
        # 2. SOMNOLENCIA FRECUENTE → Vibración
        elif drowsiness_count_2min >= 2:
            if state.can_send_intervention("vibration", 2):  # Cooldown de 2 minutos para vibraciones
                state.record_intervention("vibration")
                return EmotionAnalyzerService._create_intervention(
                    state, "vibration_only",
                    None,
                    "drowsiness",
                    metric_value=drowsiness_metric,
                    confidence=0.85
                )
        
        return None
    
    @staticmethod
    def _create_intervention(
        state: EmotionState,
        intervention_type: str,
        display_text: Optional[str],
        metric_name: str,
        video_url: Optional[str] = None,
        vibration: bool = False,
        metric_value: float = 0.0,
        confidence: float = 0.0
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
            metric_value=metric_value,
            confidence=confidence,
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