import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 3003))
    
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
    DB_SCHEMA_SESSION = os.getenv("DB_SCHEMA_SESSION", "session_service_test")
    DB_SCHEMA_MONITORING = os.getenv("DB_SCHEMA_MONITORING", "monitoring_service_test")
    
    MODELS_PATH = os.getenv("MODELS_PATH", "../models")

config = Config()