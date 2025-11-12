from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .core.config import get_settings
settings = get_settings()
class Base(DeclarativeBase): ...
engine = create_engine(settings.DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()