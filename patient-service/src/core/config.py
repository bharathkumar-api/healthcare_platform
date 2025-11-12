from pydantic import BaseModel
from dotenv import load_dotenv
import os
from functools import lru_cache
load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "Healthcare - Patient Service"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("DB_HOST", "postgres")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "healthcare_patient")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "CHANGE_ME")
    JWT_ALGORITHM: str = "HS256"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

@lru_cache
def get_settings() -> Settings:
    return Settings()