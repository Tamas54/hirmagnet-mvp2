import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from config.settings import DATABASE_URL
from database.models import Base

# Adatbázis engine létrehozása
if os.environ.get("RENDER"):
    # CRITICAL FIX: NullPool for SQLite production - NO CONNECTION POOL
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # !!!!! CRÍTICO: NullPool = zero connection pooling
        connect_args={
            "check_same_thread": False,
            "timeout": 60
        },
        echo=False
    )
    print("🚀 Production SQLite config: NullPool - No connection pool")
else:
    # Development: normál konfiguráció  
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    print("🔧 Development database config loaded")

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Adatbázis táblák létrehozása"""
    # Mappák létrehozása ha nem léteznek
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("static/audio", exist_ok=True)
    
    Base.metadata.create_all(bind=engine)
    print("✅ Adatbázis táblák létrehozva")

def get_db():
    """Adatbázis session lekérése (FastAPI dependency)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Egyszerű DB session (scriptekhez)"""
    return SessionLocal()

# Kezdeti setup futtatása
if __name__ == "__main__":
    create_tables()
