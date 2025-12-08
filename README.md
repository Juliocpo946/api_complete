# API Complete - Instalación

## Requisitos
- Python 3.8+
- MySQL

## Instalación por servicio

### 1. Gateway
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Session Service
```bash
cd session-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 3. Monitoring Service
```bash
cd monitoring-service
python -m venv venv
venv\Scripts\activate
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
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 3001
```

### Terminal 2 - Monitoring Service
```bash
cd monitoring-service
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 3002
```

### Terminal 3 - Gateway
```bash
venv\Scripts\activate
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 3000
```

## URLs de Acceso

- Gateway: http://localhost:3000
- Session Service: http://localhost:3001
- Monitoring Service: http://localhost:3002