from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys

# Debug: Print all environment variables
print("=" * 80)
print("ENVIRONMENT VARIABLES:")
for key, value in os.environ.items():
    if 'DATABASE' in key or 'POSTGRES' in key:
        print(f"  {key} = {value}")
print("=" * 80)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is not set!")
    print("Available env vars:", list(os.environ.keys()))
    sys.exit(1)

print(f"Connecting to database: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
