import pandas as pd
import numpy as np

def calculate_engagement_score(df):
    engagement_map = {'high': 3, 'medium': 2, 'low': 1}
    return df['engagement_level'].map(engagement_map).fillna(1)

def calculate_completion_rate(completed, total):
    if total == 0:
        return 0
    return completed / total

def normalize_timestamp_features(df):
    df['hour'] = pd.to_datetime(df['created_at']).dt.hour
    df['day_of_week'] = pd.to_datetime(df['created_at']).dt.dayofweek
    return df

def create_interaction_features(df):
    df['frustration_x_distraction'] = df['avg_frustration'] * df['distraction_events_per_hour']
    df['attention_x_completion'] = df['avg_visual_attention'] * df['completion_rate']
    return df

def calculate_intervention_response(interventions_df, summaries_df):
    response_rates = {}
    
    for intervention_type in ['video_instruction', 'text_instruction', 'vibration_only']:
        type_interventions = interventions_df[interventions_df['intervention_type'] == intervention_type]
        
        improvements = 0
        total = len(type_interventions)
        
        for _, intervention in type_interventions.iterrows():
            activity_uuid = intervention['activity_uuid']
            intervention_time = pd.to_datetime(intervention['timestamp'])
            
            activity_summaries = summaries_df[summaries_df['activity_uuid'] == activity_uuid].sort_values('minute_number')
            
            before_summaries = activity_summaries[pd.to_datetime(activity_summaries['timestamp']) < intervention_time]
            after_summaries = activity_summaries[pd.to_datetime(activity_summaries['timestamp']) > intervention_time]
            
            if len(before_summaries) > 0 and len(after_summaries) > 0:
                avg_engagement_before = calculate_engagement_score(before_summaries).mean()
                avg_engagement_after = calculate_engagement_score(after_summaries).mean()
                
                if avg_engagement_after > avg_engagement_before:
                    improvements += 1
        
        response_rates[intervention_type] = improvements / total if total > 0 else 0
    
    return response_rates