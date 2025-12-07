import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_KEY = os.getenv("API_KEY", "test_api_key_12345")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8001))
    GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:3000")
    
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/session_service_test")
    
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "True").lower() == "true"
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_POOL_SIZE = int(os.getenv("SQLALCHEMY_POOL_SIZE", 10))
    SQLALCHEMY_MAX_OVERFLOW = int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 20))

config = Config()