import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://healthcare:healthcare123@localhost:5432/healthcare")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production-12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
