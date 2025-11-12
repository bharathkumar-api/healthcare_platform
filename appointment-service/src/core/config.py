from pydantic import BaseModel
from dotenv import load_dotenv; load_dotenv()
import os; from functools import lru_cache

class Settings(BaseModel):
    PROJECT_NAME: str = "Healthcare - Appointment Service"
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "postgres")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "healthcare_appointment")
    @property
    def DATABASE_URL(self): return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
@lru_cache
def get_settings(): return Settings()