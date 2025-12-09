-- Reemplazar completo 03_extract_abandonment_features.sql:

WITH user_historical_stats AS (
    SELECT 
        s.user_id,
        COUNT(DISTINCT ua.activity_uuid) as total_activities,
        SUM(CASE WHEN ua.status = 'completed' THEN 1 ELSE 0 END) as completed_activities,
        SUM(CASE WHEN ua.status = 'abandoned' THEN 1 ELSE 0 END) as abandoned_activities,
        AVG(ua.pause_count) as avg_pause_count,
        AVG(TIMESTAMPDIFF(MINUTE, ua.started_at, COALESCE(ua.completed_at, NOW()))) as avg_activity_duration
    FROM session_service_test.sessions s
    JOIN session_service_test.user_activities ua ON s.session_id = ua.session_id
    WHERE ua.started_at IS NOT NULL
    GROUP BY s.user_id
),
activity_difficulty AS (
    SELECT 
        am.external_activity_id,
        am.activity_type,
        COUNT(DISTINCT ua.activity_uuid) as times_attempted,
        SUM(CASE WHEN ua.status = 'abandoned' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) as abandonment_rate_activity,
        AVG(ua.pause_count) as avg_pauses_activity,
        CASE 
            WHEN am.activity_type IN ('tracing', 'memory_game') THEN 1
            WHEN am.activity_type IN ('spelling', 'drag_and_drop', 'matching') THEN 2
            WHEN am.activity_type IN ('multiple_choice', 'fill_in_blank') THEN 3
            WHEN am.activity_type = 'reading_comprehension' THEN 4
            ELSE 2
        END as difficulty_level
    FROM session_service_test.activity_masters am
    LEFT JOIN session_service_test.user_activities ua ON am.external_activity_id = ua.external_activity_id
    GROUP BY am.external_activity_id, am.activity_type
),
user_cluster_info AS (
    SELECT 
        s.user_id,
        AVG(CASE WHEN ms.predominant_emotion = 'Angry' THEN ms.emotion_confidence_avg ELSE 0 END) as avg_frustration,
        AVG(ms.looking_screen_percentage) / 100 as completion_rate,
        SUM(ms.distraction_count) / NULLIF(SUM(TIMESTAMPDIFF(HOUR, ua.started_at, COALESCE(ua.completed_at, NOW()))), 0) as distraction_events_per_hour,
        SUM(CASE WHEN ms.ear_avg < 0.25 THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) as avg_visual_fatigue
    FROM session_service_test.sessions s
    JOIN session_service_test.user_activities ua ON s.session_id = ua.session_id
    JOIN monitoring_service_test.minute_summaries ms ON ua.activity_uuid = ms.activity_uuid
    GROUP BY s.user_id
)
SELECT 
    ua.activity_uuid,
    s.user_id,
    ua.external_activity_id,
    CASE WHEN ua.status = 'abandoned' THEN 1 ELSE 0 END as abandoned,
    
    COALESCE(uhs.completed_activities / NULLIF(uhs.total_activities, 0), 0) as historical_completion_rate,
    COALESCE(uhs.abandoned_activities / NULLIF(uhs.total_activities, 0), 0) as historical_abandonment_rate,
    COALESCE(uhs.avg_pause_count, 0) as historical_avg_pause_count,
    COALESCE(uhs.avg_activity_duration, 0) as historical_avg_duration,
    
    COALESCE(ad.difficulty_level, 2) as difficulty_level,
    COALESCE(ad.abandonment_rate_activity, 0) as activity_abandonment_rate,
    COALESCE(ad.avg_pauses_activity, 0) as avg_pauses_activity,
    
    HOUR(ua.started_at) as hour_of_day,
    DAYOFWEEK(ua.started_at) as day_of_week,
    0 as days_since_last_activity,
    3 as avg_days_between_sessions,
    
    ua.pause_count as current_pause_count,
    
    COALESCE(uci.completion_rate, 0) as cluster_completion_rate,
    COALESCE(1 - uci.completion_rate, 0) as cluster_abandonment_rate,
    COALESCE(uci.avg_frustration, 0) as avg_frustration,
    COALESCE(uci.avg_visual_fatigue, 0) as avg_visual_fatigue,
    COALESCE(uci.distraction_events_per_hour, 0) as distraction_events_per_hour
    
FROM session_service_test.user_activities ua
JOIN session_service_test.sessions s ON ua.session_id = s.session_id
LEFT JOIN user_historical_stats uhs ON s.user_id = uhs.user_id
LEFT JOIN activity_difficulty ad ON ua.external_activity_id = ad.external_activity_id
LEFT JOIN user_cluster_info uci ON s.user_id = uci.user_id
WHERE ua.started_at IS NOT NULL
ORDER BY s.user_id, ua.started_at DESC;