# Analytics ML - Clustering de Usuarios

Sistema de clustering para identificar tipos de usuarios en plataforma educativa para personas sordas.

## Estructura del Proyecto
```
analytics-ml/
├── data/
│   ├── 01_generate_fake_data.sql          # Generación de datos simulados
│   └── 02_extract_features.sql            # Extracción de features
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb      # EDA
│   ├── 02_clustering_user_types.ipynb     # Clustering con datos fake
│   └── 03_clustering_real_training.ipynb  # Clustering con datos reales
├── scripts/
│   ├── database_connection.py             # Conexión MySQL
│   ├── data_loader.py                     # Carga de datos
│   ├── feature_engineering.py             # Features adicionales
│   ├── generate_fake_sessions.py          # Generador de sesiones fake
│   └── predict_user_type.py               # Predicción de clusters
├── models/                                 # Modelos entrenados (.pkl)
├── output/                                 # Visualizaciones y reportes
└── requirements.txt
```

## Setup

### 1. Crear entorno virtual
```bash
cd ml
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar base de datos

Crear archivo `.env`:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_SCHEMA_SESSION=session_service_test
DB_SCHEMA_MONITORING=monitoring_service_test
```

### 4. Generar datos fake
```bash
# Ejecutar SQL de activities
mysql -u root -p session_service_test < data/01_generate_fake_data.sql

# Generar sesiones y datos de monitoring
python scripts/generate_fake_sessions.py
```

## Uso

### Análisis Exploratorio
```bash
jupyter notebook notebooks/01_exploratory_analysis.ipynb
```

### Entrenar Modelo (Datos Fake)
```bash
jupyter notebook notebooks/02_clustering_user_types.ipynb
```

### Predicción
```python
from scripts.predict_user_type import predict_cluster

features = {
    'completion_rate': 0.75,
    'avg_frustration': 0.45,
    'avg_visual_attention': 78.5,
    # ... resto de features
}

result = predict_cluster(features)
print(result)
# {'cluster_id': 0, 'cluster_name': 'Rápido Visual', 'confidence': 0.87}
```

## Clusters Identificados

### 1. Rápido Visual (25%)
- Alta completion_rate (>75%)
- Baja frustración (<0.4)
- Alta atención visual (>80%)

### 2. Lector Constante (30%)
- Tolera frustración (0.4-0.7)
- Buena completion_rate (60-80%)
- Pausas estratégicas

### 3. Disperso Visual (30%)
- Alta distracción (>8 eventos/hora)
- Baja completion_rate (<50%)
- Muchas pausas (>5)

### 4. Fatigado Visual (15%)
- Alta fatiga visual (EAR bajo)
- Pausas frecuentes (>6)
- Mejor en sesiones cortas

## Migración a Datos Reales

Cuando tengas 50+ usuarios reales con 5+ actividades:
```bash
jupyter notebook notebooks/03_clustering_real_training.ipynb
```

El modelo entrenado con datos reales reemplazará automáticamente al modelo fake.

## Archivos Importantes

- `models/user_type_classifier.pkl` - Modelo K-Means entrenado
- `models/scaler.pkl` - StandardScaler para normalización
- `models/cluster_labels.json` - Mapeo de IDs a nombres
- `output/users_with_clusters.csv` - Usuarios clasificados

## Métricas del Modelo

- Silhouette Score: 0.45+ (buena separación)
- Davies-Bouldin: <1.5 (clusters compactos)
- K óptimo: 4 clusters

## Próximos Pasos

1. Integrar predicción en monitoring-service
2. Ajustar umbrales de intervención por cluster
3. Reentrenar modelo mensualmente con datos reales
4. Validar mejoras en engagement y completion_rate

## Soporte

Para preguntas o issues, contactar al equipo de desarrollo.