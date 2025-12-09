import joblib
import numpy as np
import json
import os
from pathlib import Path
from src.config.config import config
from src.database.database_connection import execute_query

class PredictionService:
    
    @staticmethod
    def load_model():
        model_path = Path(config.MODELS_PATH) / 'user_type_classifier.pkl'
        scaler_path = Path(config.MODELS_PATH) / 'scaler.pkl'
        labels_path = Path(config.MODELS_PATH) / 'cluster_labels.json'
        
        if not model_path.exists():
            raise FileNotFoundError("Modelo no encontrado")
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        with open(labels_path, 'r') as f:
            labels = json.load(f)
        
        return model, scaler, labels
    
    @staticmethod
    def predict_cluster(user_features: dict) -> dict:
        model, scaler, labels = PredictionService.load_model()
        
        feature_order = [
            'completion_rate',
            'abandonment_rate',
            'avg_frustration',
            'avg_visual_attention',
            'avg_visual_fatigue',
            'distraction_events_per_hour',
            'drowsiness_events_per_hour',
            'avg_pause_count',
            'intervention_count_per_activity',
            'avg_engagement_score',
            'response_to_video',
            'response_to_text',
            'response_to_vibration',
            'avg_activity_duration_minutes',
            'preference_easy_activities'
        ]
        
        features_array = np.array([[user_features.get(f, 0) for f in feature_order]])
        features_scaled = scaler.transform(features_array)
        
        cluster_id = model.predict(features_scaled)[0]
        distances = model.transform(features_scaled)[0]
        confidence = 1 - (distances[cluster_id] / distances.sum())
        
        cluster_name = labels.get(str(cluster_id), f"Cluster {cluster_id}")
        
        return {
            'cluster_id': int(cluster_id),
            'cluster_name': cluster_name,
            'confidence': float(confidence)
        }
    
    @staticmethod
    def predict_from_user_id(user_id: int) -> dict:
        query = f"""
        WITH user_activity_stats AS (
            SELECT 
                s.user_id,
                COUNT(DISTINCT ua.activity_uuid) as total_activities,
                SUM(CASE WHEN ua.status = 'completed' THEN 1 ELSE 0 END) as completed_activities,
                SUM(CASE WHEN ua.status = 'abandoned' THEN 1 ELSE 0 END) as abandoned_activities,
                AVG(ua.pause_count) as avg_pause_count,
                AVG(TIMESTAMPDIFF(MINUTE, ua.started_at, ua.completed_at)) as avg_activity_duration_minutes
            FROM {config.DB_SCHEMA_SESSION}.sessions s
            JOIN {config.DB_SCHEMA_SESSION}.user_activities ua ON s.session_id = ua.session_id
            WHERE s.user_id = {user_id}
            AND ua.started_at IS NOT NULL
            GROUP BY s.user_id
        ),
        emotion_stats AS (
            SELECT 
                s.user_id,
                AVG(CASE WHEN ms.predominant_emotion = 'Angry' THEN ms.emotion_confidence_avg ELSE 0 END) as avg_frustration,
                AVG(ms.looking_screen_percentage) as avg_visual_attention,
                AVG(CASE WHEN ms.engagement_level = 'high' THEN 3 
                         WHEN ms.engagement_level = 'medium' THEN 2 
                         ELSE 1 END) as avg_engagement_score
            FROM {config.DB_SCHEMA_SESSION}.sessions s
            JOIN {config.DB_SCHEMA_SESSION}.user_activities ua ON s.session_id = ua.session_id
            JOIN {config.DB_SCHEMA_MONITORING}.minute_summaries ms ON ua.activity_uuid = ms.activity_uuid
            WHERE s.user_id = {user_id}
            GROUP BY s.user_id
        ),
        distraction_stats AS (
            SELECT 
                s.user_id,
                SUM(ms.distraction_count) as total_distraction_events,
                SUM(ms.drowsiness_count) as total_drowsiness_events,
                SUM(TIMESTAMPDIFF(HOUR, ua.started_at, COALESCE(ua.completed_at, NOW()))) as total_hours
            FROM {config.DB_SCHEMA_SESSION}.sessions s
            JOIN {config.DB_SCHEMA_SESSION}.user_activities ua ON s.session_id = ua.session_id
            JOIN {config.DB_SCHEMA_MONITORING}.minute_summaries ms ON ua.activity_uuid = ms.activity_uuid
            WHERE s.user_id = {user_id}
            GROUP BY s.user_id
        ),
        intervention_stats AS (
            SELECT 
                s.user_id,
                COUNT(i.packet_id) as total_interventions,
                SUM(CASE WHEN i.intervention_type = 'video_instruction' THEN 1 ELSE 0 END) as video_interventions,
                SUM(CASE WHEN i.intervention_type = 'text_instruction' THEN 1 ELSE 0 END) as text_interventions,
                SUM(CASE WHEN i.intervention_type = 'vibration_only' THEN 1 ELSE 0 END) as vibration_interventions
            FROM {config.DB_SCHEMA_SESSION}.sessions s
            JOIN {config.DB_SCHEMA_SESSION}.user_activities ua ON s.session_id = ua.session_id
            JOIN {config.DB_SCHEMA_MONITORING}.interventions i ON ua.activity_uuid = i.activity_uuid
            WHERE s.user_id = {user_id}
            GROUP BY s.user_id
        ),
        activity_type_performance AS (
            SELECT 
                s.user_id,
                SUM(CASE WHEN am.activity_type IN ('tracing', 'memory_game') AND ua.status = 'completed' THEN 1 ELSE 0 END) as easy_completed,
                SUM(CASE WHEN am.activity_type IN ('tracing', 'memory_game') THEN 1 ELSE 0 END) as easy_total
            FROM {config.DB_SCHEMA_SESSION}.sessions s
            JOIN {config.DB_SCHEMA_SESSION}.user_activities ua ON s.session_id = ua.session_id
            JOIN {config.DB_SCHEMA_SESSION}.activity_masters am ON ua.external_activity_id = am.external_activity_id
            WHERE s.user_id = {user_id}
            GROUP BY s.user_id
        ),
        visual_fatigue_stats AS (
            SELECT 
                s.user_id,
                SUM(CASE WHEN ms.ear_avg < 0.25 THEN 1 ELSE 0 END) as low_ear_count,
                COUNT(*) as total_minutes
            FROM {config.DB_SCHEMA_SESSION}.sessions s
            JOIN {config.DB_SCHEMA_SESSION}.user_activities ua ON s.session_id = ua.session_id
            JOIN {config.DB_SCHEMA_MONITORING}.minute_summaries ms ON ua.activity_uuid = ms.activity_uuid
            WHERE s.user_id = {user_id}
            GROUP BY s.user_id
        )
        SELECT 
            uas.user_id,
            COALESCE(uas.completed_activities / NULLIF(uas.total_activities, 0), 0) as completion_rate,
            COALESCE(uas.abandoned_activities / NULLIF(uas.total_activities, 0), 0) as abandonment_rate,
            COALESCE(es.avg_frustration, 0) as avg_frustration,
            COALESCE(es.avg_visual_attention, 0) as avg_visual_attention,
            COALESCE(vfs.low_ear_count / NULLIF(vfs.total_minutes, 0), 0) as avg_visual_fatigue,
            COALESCE(ds.total_distraction_events / NULLIF(ds.total_hours, 0), 0) as distraction_events_per_hour,
            COALESCE(ds.total_drowsiness_events / NULLIF(ds.total_hours, 0), 0) as drowsiness_events_per_hour,
            COALESCE(uas.avg_pause_count, 0) as avg_pause_count,
            COALESCE(is_total.total_interventions / NULLIF(uas.total_activities, 0), 0) as intervention_count_per_activity,
            COALESCE(es.avg_engagement_score, 1) as avg_engagement_score,
            COALESCE(is_total.video_interventions / NULLIF(is_total.total_interventions, 0), 0) as response_to_video,
            COALESCE(is_total.text_interventions / NULLIF(is_total.total_interventions, 0), 0) as response_to_text,
            COALESCE(is_total.vibration_interventions / NULLIF(is_total.total_interventions, 0), 0) as response_to_vibration,
            COALESCE(uas.avg_activity_duration_minutes, 0) as avg_activity_duration_minutes,
            COALESCE(atp.easy_completed / NULLIF(atp.easy_total, 0), 0) as preference_easy_activities
        FROM user_activity_stats uas
        LEFT JOIN emotion_stats es ON uas.user_id = es.user_id
        LEFT JOIN distraction_stats ds ON uas.user_id = ds.user_id
        LEFT JOIN intervention_stats is_total ON uas.user_id = is_total.user_id
        LEFT JOIN activity_type_performance atp ON uas.user_id = atp.user_id
        LEFT JOIN visual_fatigue_stats vfs ON uas.user_id = vfs.user_id
        WHERE uas.total_activities > 0
        """
        
        result = execute_query(query)
        
        if not result:
            raise ValueError(f"No se encontraron datos para user_id {user_id}")
        
        user_features = result[0]
        
        return PredictionService.predict_cluster(user_features)
    
    @staticmethod
    def get_cluster_distribution():
        metadata_path = Path(config.MODELS_PATH) / 'model_metadata.json'
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        return {
            'distribution': metadata.get('cluster_distribution', {}),
            'total_users': sum(metadata.get('cluster_distribution', {}).values())
        }
    
    @staticmethod
    def get_model_metadata():
        metadata_path = Path(config.MODELS_PATH) / 'model_metadata.json'
        
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        return metadata