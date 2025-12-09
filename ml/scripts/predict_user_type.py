import joblib
import numpy as np
import json
from pathlib import Path

MODEL_PATH = Path('../models/user_type_classifier.pkl')
SCALER_PATH = Path('../models/scaler.pkl')
LABELS_PATH = Path('../models/cluster_labels.json')

def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Modelo no encontrado. Ejecuta el notebook de clustering primero.")
    
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    
    with open(LABELS_PATH, 'r') as f:
        labels = json.load(f)
    
    return model, scaler, labels

def predict_cluster(user_features):
    model, scaler, labels = load_model()
    
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

def predict_from_user_id(user_id):
    from data_loader import execute_query
    
    query = f"""
    -- (usar el mismo query de 02_extract_features.sql pero con WHERE user_id = {user_id})
    """
    
    result = execute_query(query)
    
    if not result:
        raise ValueError(f"No se encontraron datos para user_id {user_id}")
    
    user_features = result[0]
    
    return predict_cluster(user_features)

if __name__ == "__main__":
    example_features = {
        'completion_rate': 0.65,
        'abandonment_rate': 0.35,
        'avg_frustration': 0.75,
        'avg_visual_attention': 68.5,
        'avg_visual_fatigue': 0.15,
        'distraction_events_per_hour': 8.2,
        'drowsiness_events_per_hour': 2.1,
        'avg_pause_count': 5.3,
        'intervention_count_per_activity': 1.8,
        'avg_engagement_score': 1.8,
        'response_to_video': 0.35,
        'response_to_text': 0.25,
        'response_to_vibration': 0.40,
        'avg_activity_duration_minutes': 8.5,
        'preference_easy_activities': 0.70
    }
    
    result = predict_cluster(example_features)
    print(json.dumps(result, indent=2))