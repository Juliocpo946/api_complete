import joblib
import numpy as np
import json
from pathlib import Path
from src.config.config import config
from src.database.database_connection import execute_query

class AbandonmentService:
    
    @staticmethod
    def load_model():
        model_path = Path(config.MODELS_PATH) / 'abandonment_classifier.pkl'
        scaler_path = Path(config.MODELS_PATH) / 'abandonment_scaler.pkl'
        labels_path = Path(config.MODELS_PATH) / 'abandonment_metadata.json'
        
        if not model_path.exists():
            raise FileNotFoundError("Modelo de abandonment no encontrado")
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        with open(labels_path, 'r') as f:
            metadata = json.load(f)
        
        return model, scaler, metadata
    
    @staticmethod
    def predict_abandonment(user_features: dict) -> dict:
        model, scaler, metadata = AbandonmentService.load_model()
        
        feature_order = metadata['features']
        features_array = np.array([[user_features.get(f, 0) for f in feature_order]])
        features_scaled = scaler.transform(features_array)
        
        probability = model.predict_proba(features_scaled)[0][1]
        prediction = model.predict(features_scaled)[0]
        
        risk_level = 'HIGH' if probability > 0.7 else 'MEDIUM' if probability > 0.4 else 'LOW'
        
        return {
            'will_abandon': bool(prediction),
            'abandonment_probability': float(probability),
            'risk_level': risk_level,
            'recommendation': AbandonmentService._get_recommendation(probability, user_features)
        }
    
    @staticmethod
    def _get_recommendation(probability: float, features: dict) -> str:
        if probability > 0.7:
            if features.get('difficulty_level', 2) >= 3:
                return "Alta probabilidad de abandono. Sugerir actividad más fácil."
            elif features.get('current_pause_count', 0) > 5:
                return "Alta probabilidad de abandono. Usuario fatigado, sugerir descanso."
            else:
                return "Alta probabilidad de abandono. Enviar video de ayuda inmediatamente."
        
        elif probability > 0.4:
            if features.get('days_since_last_activity', 0) > 3:
                return "Probabilidad media de abandono. Usuario inactivo, enviar recordatorio."
            else:
                return "Probabilidad media de abandono. Monitorear de cerca y preparar intervención."
        
        else:
            return "Baja probabilidad de abandono. Usuario estable."
    
    @staticmethod
    def predict_for_user_activity(user_id: int, external_activity_id: int) -> dict:
        query = f"""
        WITH user_historical_stats AS (
            SELECT 
                s.user_id,
                COUNT(DISTINCT ua.activity_uuid) as total_activities,
                SUM(CASE WHEN ua.status = 'completed' THEN 1 ELSE 0 END) as completed_activities,
                SUM(CASE WHEN ua.status = 'abandoned' THEN 1 ELSE 0 END) as abandoned_activities,
                AVG(ua.pause_count) as avg_pause_count,
                AVG(TIMESTAMPDIFF(MINUTE, ua.started_at, COALESCE(ua.completed_at, NOW()))) as avg_activity_duration
            FROM {config.DB_SCHEMA_SESSION}.sessions s
            JOIN {config.DB_SCHEMA_SESSION}.user_activities ua ON s.session_id = ua.session_id
            WHERE s.user_id = {user_id}
            AND ua.started_at IS NOT NULL
            GROUP BY s.user_id
        ),
        activity_difficulty AS (
            SELECT 
                am.external_activity_id,
                am.activity_type,
                SUM(CASE WHEN ua.status = 'abandoned' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) as abandonment_rate_activity,
                AVG(ua.pause_count) as avg_pauses_activity,
                CASE 
                    WHEN am.activity_type IN ('tracing', 'memory_game') THEN 1
                    WHEN am.activity_type IN ('spelling', 'drag_and_drop', 'matching') THEN 2
                    WHEN am.activity_type IN ('multiple_choice', 'fill_in_blank') THEN 3
                    WHEN am.activity_type = 'reading_comprehension' THEN 4
                    ELSE 2
                END as difficulty_level
            FROM {config.DB_SCHEMA_SESSION}.activity_masters am
            LEFT JOIN {config.DB_SCHEMA_SESSION}.user_activities ua ON am.external_activity_id = ua.external_activity_id
            WHERE am.external_activity_id = {external_activity_id}
            GROUP BY am.external_activity_id, am.activity_type
        ),
        user_cluster_info AS (
            SELECT 
                s.user_id,
                AVG(CASE WHEN ms.predominant_emotion = 'Angry' THEN ms.emotion_confidence_avg ELSE 0 END) as avg_frustration,
                AVG(ms.looking_screen_percentage) / 100 as completion_rate,
                SUM(ms.distraction_count) / NULLIF(SUM(TIMESTAMPDIFF(HOUR, ua.started_at, COALESCE(ua.completed_at, NOW()))), 0) as distraction_events_per_hour,
                SUM(CASE WHEN ms.ear_avg < 0.25 THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) as avg_visual_fatigue
            FROM {config.DB_SCHEMA_SESSION}.sessions s
            JOIN {config.DB_SCHEMA_SESSION}.user_activities ua ON s.session_id = ua.session_id
            JOIN {config.DB_SCHEMA_MONITORING}.minute_summaries ms ON ua.activity_uuid = ms.activity_uuid
            WHERE s.user_id = {user_id}
            GROUP BY s.user_id
        ),
        recent_session AS (
            SELECT 
                s.user_id,
                MAX(ua.started_at) as last_activity_time,
                TIMESTAMPDIFF(DAY, MAX(ua.started_at), NOW()) as days_since_last_activity
            FROM {config.DB_SCHEMA_SESSION}.sessions s
            JOIN {config.DB_SCHEMA_SESSION}.user_activities ua ON s.session_id = ua.session_id
            WHERE s.user_id = {user_id}
            GROUP BY s.user_id
        )
        SELECT 
            uhs.user_id,
            uhs.completed_activities / NULLIF(uhs.total_activities, 0) as historical_completion_rate,
            uhs.abandoned_activities / NULLIF(uhs.total_activities, 0) as historical_abandonment_rate,
            uhs.avg_pause_count as historical_avg_pause_count,
            uhs.avg_activity_duration as historical_avg_duration,
            ad.difficulty_level,
            COALESCE(ad.abandonment_rate_activity, 0) as activity_abandonment_rate,
            COALESCE(ad.avg_pauses_activity, 0) as avg_pauses_activity,
            HOUR(NOW()) as hour_of_day,
            DAYOFWEEK(NOW()) as day_of_week,
            COALESCE(rs.days_since_last_activity, 0) as days_since_last_activity,
            3 as avg_days_between_sessions,
            0 as current_pause_count,
            COALESCE(uci.completion_rate, 0) as cluster_completion_rate,
            1 - COALESCE(uci.completion_rate, 0) as cluster_abandonment_rate,
            COALESCE(uci.avg_frustration, 0) as avg_frustration,
            COALESCE(uci.avg_visual_fatigue, 0) as avg_visual_fatigue,
            COALESCE(uci.distraction_events_per_hour, 0) as distraction_events_per_hour
        FROM user_historical_stats uhs
        CROSS JOIN activity_difficulty ad
        LEFT JOIN user_cluster_info uci ON uhs.user_id = uci.user_id
        LEFT JOIN recent_session rs ON uhs.user_id = rs.user_id
        """
        
        result = execute_query(query)
        
        if not result:
            raise ValueError(f"No se encontraron datos para user_id {user_id}")
        
        user_features = result[0]
        
        return AbandonmentService.predict_abandonment(user_features)