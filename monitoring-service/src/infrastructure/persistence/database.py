from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from src.infrastructure.config.config import config

engine = create_engine(
    config.DATABASE_URL,
    echo=config.SQLALCHEMY_ECHO,
    pool_pre_ping=config.SQLALCHEMY_POOL_PRE_PING,
    pool_size=config.SQLALCHEMY_POOL_SIZE,
    max_overflow=config.SQLALCHEMY_MAX_OVERFLOW
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    print("[DATABASE] Tablas inicializadas exitosamente")