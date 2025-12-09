-- ============================================
-- QUERY DE EXTRACCIÓN DE FEATURES
-- ============================================

WITH user_activity_stats AS (
    SELECT 
        s.user_id,
        COUNT(DISTINCT ua.activity_uuid) as total_activities,
        SUM(CASE WHEN ua.status = 'completed' THEN 1 ELSE 0 END) as completed_activities,
        SUM(CASE WHEN ua.status = 'abandoned' THEN 1 ELSE 0 END) as abandoned_activities,
        AVG(ua.pause_count) as avg_pause_count,
        AVG(TIMESTAMPDIFF(MINUTE, ua.started_at, ua.completed_at)) as avg_activity_duration_minutes
    FROM session_service_test.sessions s
    JOIN session_service_test.user_activities ua ON s.session_id = ua.session_id
    WHERE ua.started_at IS NOT NULL
    GROUP BY s.user_id
),
emotion_stats AS (
    SELECT 
        s.user_id,
        AVG(CASE WHEN ms.predominant_emotion = 'Angry' THEN ms.emotion_confidence_avg ELSE 0 END) as avg_frustration,
        AVG(ms.looking_screen_percentage) as avg_visual_attention,
        AVG(ms.ear_avg) as avg_ear,
        AVG(CASE WHEN ms.engagement_level = 'high' THEN 3 
                 WHEN ms.engagement_level = 'medium' THEN 2 
                 ELSE 1 END) as avg_engagement_score
    FROM session_service_test.sessions s
    JOIN session_service_test.user_activities ua ON s.session_id = ua.session_id
    JOIN monitoring_service_test.minute_summaries ms ON ua.activity_uuid = ms.activity_uuid
    GROUP BY s.user_id
),
distraction_stats AS (
    SELECT 
        s.user_id,
        SUM(ms.distraction_count) as total_distraction_events,
        SUM(ms.drowsiness_count) as total_drowsiness_events,
        SUM(TIMESTAMPDIFF(HOUR, ua.started_at, COALESCE(ua.completed_at, NOW()))) as total_hours
    FROM session_service_test.sessions s
    JOIN session_service_test.user_activities ua ON s.session_id = ua.session_id
    JOIN monitoring_service_test.minute_summaries ms ON ua.activity_uuid = ms.activity_uuid
    GROUP BY s.user_id
),
intervention_stats AS (
    SELECT 
        s.user_id,
        COUNT(i.packet_id) as total_interventions,
        SUM(CASE WHEN i.intervention_type = 'video_instruction' THEN 1 ELSE 0 END) as video_interventions,
        SUM(CASE WHEN i.intervention_type = 'text_instruction' THEN 1 ELSE 0 END) as text_interventions,
        SUM(CASE WHEN i.intervention_type = 'vibration_only' THEN 1 ELSE 0 END) as vibration_interventions
    FROM session_service_test.sessions s
    JOIN session_service_test.user_activities ua ON s.session_id = ua.session_id
    JOIN monitoring_service_test.interventions i ON ua.activity_uuid = i.activity_uuid
    GROUP BY s.user_id
),
activity_type_performance AS (
    SELECT 
        s.user_id,
        SUM(CASE WHEN am.activity_type IN ('tracing', 'memory_game') AND ua.status = 'completed' THEN 1 ELSE 0 END) as easy_completed,
        SUM(CASE WHEN am.activity_type IN ('tracing', 'memory_game') THEN 1 ELSE 0 END) as easy_total,
        SUM(CASE WHEN am.activity_type IN ('fill_in_blank', 'reading_comprehension') AND ua.status = 'completed' THEN 1 ELSE 0 END) as hard_completed,
        SUM(CASE WHEN am.activity_type IN ('fill_in_blank', 'reading_comprehension') THEN 1 ELSE 0 END) as hard_total
    FROM session_service_test.sessions s
    JOIN session_service_test.user_activities ua ON s.session_id = ua.session_id
    JOIN session_service_test.activity_masters am ON ua.external_activity_id = am.external_activity_id
    GROUP BY s.user_id
),
visual_fatigue_stats AS (
    SELECT 
        s.user_id,
        SUM(CASE WHEN ms.ear_avg < 0.25 THEN 1 ELSE 0 END) as low_ear_count,
        COUNT(*) as total_minutes
    FROM session_service_test.sessions s
    JOIN session_service_test.user_activities ua ON s.session_id = ua.session_id
    JOIN monitoring_service_test.minute_summaries ms ON ua.activity_uuid = ms.activity_uuid
    GROUP BY s.user_id
)
SELECT 
    uas.user_id,
    
    -- Completion metrics
    COALESCE(uas.completed_activities / NULLIF(uas.total_activities, 0), 0) as completion_rate,
    COALESCE(uas.abandoned_activities / NULLIF(uas.total_activities, 0), 0) as abandonment_rate,
    
    -- Emotion metrics
    COALESCE(es.avg_frustration, 0) as avg_frustration,
    COALESCE(es.avg_visual_attention, 0) as avg_visual_attention,
    COALESCE(es.avg_engagement_score, 1) as avg_engagement_score,
    
    -- Distraction metrics
    COALESCE(ds.total_distraction_events / NULLIF(ds.total_hours, 0), 0) as distraction_events_per_hour,
    COALESCE(ds.total_drowsiness_events / NULLIF(ds.total_hours, 0), 0) as drowsiness_events_per_hour,
    
    -- Visual fatigue
    COALESCE(vfs.low_ear_count / NULLIF(vfs.total_minutes, 0), 0) as avg_visual_fatigue,
    
    -- Pause metrics
    COALESCE(uas.avg_pause_count, 0) as avg_pause_count,
    
    -- Duration metrics
    COALESCE(uas.avg_activity_duration_minutes, 0) as avg_activity_duration_minutes,
    
    -- Intervention metrics
    COALESCE(is_total.total_interventions / NULLIF(uas.total_activities, 0), 0) as intervention_count_per_activity,
    COALESCE(is_total.video_interventions / NULLIF(is_total.total_interventions, 0), 0) as response_to_video,
    COALESCE(is_total.text_interventions / NULLIF(is_total.total_interventions, 0), 0) as response_to_text,
    COALESCE(is_total.vibration_interventions / NULLIF(is_total.total_interventions, 0), 0) as response_to_vibration,
    
    -- Activity difficulty preference
    COALESCE(atp.easy_completed / NULLIF(atp.easy_total, 0), 0) as preference_easy_activities,
    COALESCE(atp.hard_completed / NULLIF(atp.hard_total, 0), 0) as performance_hard_activities
    
FROM user_activity_stats uas
LEFT JOIN emotion_stats es ON uas.user_id = es.user_id
LEFT JOIN distraction_stats ds ON uas.user_id = ds.user_id
LEFT JOIN intervention_stats is_total ON uas.user_id = is_total.user_id
LEFT JOIN activity_type_performance atp ON uas.user_id = atp.user_id
LEFT JOIN visual_fatigue_stats vfs ON uas.user_id = vfs.user_id
WHERE uas.total_activities > 0
ORDER BY uas.user_id;