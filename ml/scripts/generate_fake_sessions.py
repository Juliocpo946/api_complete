import pymysql
import random
from datetime import datetime, timedelta
from database_connection import get_connection

def generate_fake_sessions_and_activities():
    connection = get_connection()
    
    try:
        with connection.cursor() as cursor:
            # Definir clusters y sus características
            clusters = {
                'rapido_visual': {
                    'users': list(range(1001, 1026)),  # 25 usuarios (25%)
                    'completion_rate': (0.75, 0.90),
                    'avg_frustration': (0.2, 0.4),
                    'distraction_rate': (1, 3),
                    'pause_count': (1, 3),
                    'sessions_per_user': (10, 15),
                    'activities_per_session': (5, 8)
                },
                'lector_constante': {
                    'users': list(range(1026, 1056)),  # 30 usuarios (30%)
                    'completion_rate': (0.60, 0.80),
                    'avg_frustration': (0.4, 0.7),
                    'distraction_rate': (3, 6),
                    'pause_count': (3, 6),
                    'sessions_per_user': (10, 15),
                    'activities_per_session': (4, 7)
                },
                'disperso_visual': {
                    'users': list(range(1056, 1086)),  # 30 usuarios (30%)
                    'completion_rate': (0.30, 0.50),
                    'avg_frustration': (0.6, 0.85),
                    'distraction_rate': (8, 15),
                    'pause_count': (5, 10),
                    'sessions_per_user': (8, 12),
                    'activities_per_session': (3, 6)
                },
                'fatigado_visual': {
                    'users': list(range(1086, 1101)),  # 15 usuarios (15%)
                    'completion_rate': (0.40, 0.60),
                    'avg_frustration': (0.5, 0.75),
                    'distraction_rate': (4, 8),
                    'pause_count': (6, 12),
                    'sessions_per_user': (8, 12),
                    'activities_per_session': (2, 5)
                }
            }
            
            activities = [101, 102, 103, 104, 105, 106, 107, 108]
            session_counter = 1
            activity_counter = 1
            
            for cluster_name, cluster_data in clusters.items():
                print(f"Generando datos para cluster: {cluster_name}")
                
                for user_id in cluster_data['users']:
                    num_sessions = random.randint(*cluster_data['sessions_per_user'])
                    
                    for session_num in range(num_sessions):
                        days_ago = random.randint(0, 30)
                        session_date = datetime.now() - timedelta(days=days_ago)
                        session_id = f"sess_{user_id}_{session_counter}"
                        session_counter += 1
                        
                        # Insertar sesión
                        cursor.execute(
                            "USE session_service_test"
                        )
                        cursor.execute(
                            """INSERT INTO sessions 
                            (session_id, user_id, disability_type, cognitive_analysis_enabled, status, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                            (session_id, user_id, 'auditiva', True, 'finalized', session_date, session_date)
                        )
                        
                        # Generar actividades para esta sesión
                        num_activities = random.randint(*cluster_data['activities_per_session'])
                        selected_activities = random.sample(activities, min(num_activities, len(activities)))
                        
                        for external_activity_id in selected_activities:
                            activity_uuid = f"act_{user_id}_{activity_counter}"
                            activity_counter += 1
                            
                            # Determinar si se completa o abandona según cluster
                            completion_prob = random.uniform(*cluster_data['completion_rate'])
                            is_completed = random.random() < completion_prob
                            
                            status = 'completed' if is_completed else 'abandoned'
                            pause_count = random.randint(*cluster_data['pause_count'])
                            
                            activity_start = session_date + timedelta(minutes=random.randint(0, 60))
                            activity_duration = random.randint(3, 20) if is_completed else random.randint(1, 8)
                            activity_end = activity_start + timedelta(minutes=activity_duration) if is_completed else None
                            
                            # Insertar actividad
                            cursor.execute(
                                """INSERT INTO user_activities 
                                (activity_uuid, session_id, external_activity_id, status, pause_count, started_at, completed_at, created_at, updated_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                (activity_uuid, session_id, external_activity_id, status, pause_count, 
                                 activity_start, activity_end, activity_start, activity_end or activity_start)
                            )
                            
                            # Insertar pause_counter
                            if pause_count > 0:
                                pause_timestamps = []
                                for p in range(pause_count):
                                    pause_time = activity_start + timedelta(minutes=random.randint(1, activity_duration))
                                    pause_timestamps.append(pause_time.isoformat())
                                
                                cursor.execute(
                                    """INSERT INTO pause_counters 
                                    (activity_uuid, pause_count, paused_timestamps, created_at, updated_at)
                                    VALUES (%s, %s, %s, %s, %s)""",
                                    (activity_uuid, pause_count, str(pause_timestamps), activity_start, activity_start)
                                )
                            
                            # Generar minute_summaries y interventions
                            generate_monitoring_data(
                                cursor, activity_uuid, session_id, activity_start, 
                                activity_duration, cluster_data, is_completed
                            )
            
            connection.commit()
            print("Datos fake generados exitosamente")
            
    finally:
        connection.close()

def generate_monitoring_data(cursor, activity_uuid, session_id, start_time, duration_minutes, cluster_data, is_completed):
    cursor.execute("USE monitoring_service_test")
    
    emotions = ['Happy', 'Neutral', 'Sad', 'Angry', 'Surprise', 'Fear']
    engagement_levels = ['high', 'medium', 'low']
    
    frustration_base = random.uniform(*cluster_data['avg_frustration'])
    distraction_base = random.uniform(*cluster_data['distraction_rate'])
    
    # Generar minute_summaries
    for minute in range(duration_minutes):
        summary_id = f"sum_{activity_uuid}_{minute}"
        timestamp = start_time + timedelta(minutes=minute)
        
        # Simular progresión de frustración (aumenta con el tiempo si no completa)
        if not is_completed and minute > duration_minutes * 0.6:
            frustration = min(0.95, frustration_base + random.uniform(0.1, 0.3))
            predominant_emotion = 'Angry'
        else:
            frustration = frustration_base + random.uniform(-0.1, 0.1)
            predominant_emotion = random.choices(
                emotions, 
                weights=[0.3, 0.3, 0.1, frustration, 0.1, 0.1]
            )[0]
        
        emotion_confidence = random.uniform(0.6, 0.95)
        ear_avg = random.uniform(0.20, 0.35)
        pitch_avg = random.uniform(-15, 15)
        yaw_avg = random.uniform(-20, 20)
        looking_screen_pct = random.uniform(60, 95) if frustration < 0.6 else random.uniform(40, 70)
        face_detected_pct = random.uniform(85, 99)
        
        distraction_count = int(distraction_base * random.uniform(0.5, 1.5)) if minute % 2 == 0 else 0
        drowsiness_count = 1 if ear_avg < 0.25 and random.random() < 0.3 else 0
        
        cognitive_state = 'focused' if frustration < 0.5 else 'frustrated'
        engagement_level = random.choices(
            engagement_levels,
            weights=[0.2, 0.5, 0.3] if frustration < 0.5 else [0.1, 0.3, 0.6]
        )[0]
        
        cursor.execute(
            """INSERT INTO minute_summaries 
            (summary_id, session_id, activity_uuid, minute_number, timestamp,
            predominant_emotion, emotion_confidence_avg, ear_avg, pitch_avg, yaw_avg,
            looking_screen_percentage, face_detected_percentage, distraction_count, 
            drowsiness_count, abrupt_changes_count, cognitive_state, engagement_level, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (summary_id, session_id, activity_uuid, minute, timestamp.isoformat(),
             predominant_emotion, emotion_confidence, ear_avg, pitch_avg, yaw_avg,
             looking_screen_pct, face_detected_pct, distraction_count, drowsiness_count,
             0, cognitive_state, engagement_level, timestamp)
        )
    
    # Generar intervenciones basadas en características del cluster
    num_interventions = random.randint(0, int(duration_minutes * 0.4))
    intervention_types = ['video_instruction', 'text_instruction', 'vibration_only', 'pause_suggestion']
    
    for i in range(num_interventions):
        packet_id = f"int_{activity_uuid}_{i}"
        intervention_minute = random.randint(2, duration_minutes - 1)
        intervention_time = start_time + timedelta(minutes=intervention_minute)
        
        if frustration_base > 0.7:
            intervention_type = random.choice(['video_instruction', 'pause_suggestion'])
        elif distraction_base > 8:
            intervention_type = 'vibration_only'
        else:
            intervention_type = random.choice(intervention_types)
        
        metric_name_map = {
            'video_instruction': 'frustration',
            'text_instruction': 'frustration',
            'vibration_only': 'distraction',
            'pause_suggestion': 'activity_duration'
        }
        
        cursor.execute(
            """INSERT INTO interventions 
            (packet_id, session_id, activity_uuid, intervention_type, video_url, display_text,
            vibration_enabled, metric_name, metric_value, confidence, duration_ms, timestamp, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (packet_id, session_id, activity_uuid, intervention_type,
             'https://example.com/video.mp4' if 'video' in intervention_type else None,
             'Texto de ayuda' if 'text' in intervention_type else None,
             intervention_type == 'vibration_only',
             metric_name_map[intervention_type],
             int(frustration_base * 100),
             int(random.uniform(75, 95)),
             5000,
             intervention_time,
             intervention_time)
        )

if __name__ == "__main__":
    generate_fake_sessions_and_activities()