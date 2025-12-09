import sys
import pandas as pd
from database_connection import execute_query

def extract_abandonment_features():
    with open('../data/03_extract_abandonment_features.sql', 'r', encoding='utf-8') as f:
        query = f.read()
    
    print("Extrayendo features de abandono desde la base de datos...")
    data = execute_query(query)
    df = pd.DataFrame(data)
    
    print(f"Registros extraídos: {len(df)}")
    print(f"Columnas: {df.shape[1]}")
    
    numeric_columns = [
        'abandoned', 'historical_completion_rate', 'historical_abandonment_rate',
        'historical_avg_pause_count', 'historical_avg_duration', 'difficulty_level',
        'activity_abandonment_rate', 'avg_pauses_activity', 'hour_of_day',
        'day_of_week', 'days_since_last_activity', 'avg_days_between_sessions',
        'current_pause_count', 'cluster_completion_rate', 'cluster_abandonment_rate',
        'avg_frustration', 'avg_visual_fatigue', 'distraction_events_per_hour'
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.fillna(0)
    
    output_path = '../output/abandonment_features.csv'
    df.to_csv(output_path, index=False)
    print(f"\nFeatures guardadas en: {output_path}")
    
    print(f"\nDistribución de la variable target:")
    print(df['abandoned'].value_counts())
    print(f"\nTasa de abandono: {df['abandoned'].mean():.2%}")
    
    return df

if __name__ == "__main__":
    df = extract_abandonment_features()
    print("\nPrimeras filas:")
    print(df.head())