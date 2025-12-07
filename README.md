# API Complete - Instalación

## Requisitos
- Python 3.8+
- MySQL

## Instalación por servicio

### 1. Gateway
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Session Service
```bash
cd session-service
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 3. Monitoring Service
```bash
cd monitoring-service
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

## Configuración de Base de Datos

Crear las bases de datos en MySQL:
```sql
CREATE DATABASE session_service_test;
CREATE DATABASE monitoring_service_test;
```

## Ejecución

### Terminal 1 - Session Service
```bash
cd session-service
source venv/bin/activate
python main.py
```

### Terminal 2 - Monitoring Service
```bash
cd monitoring-service
source venv/bin/activate
python main.py
```

### Terminal 3 - Gateway
```bash
source venv/bin/activate
python gateway.py
```

## URLs de Acceso

- Gateway: http://localhost:3000
- Session Service: http://localhost:3001
- Monitoring Service: http://localhost:3002