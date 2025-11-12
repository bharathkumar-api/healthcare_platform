from fastapi import FastAPI
from .database import Base, engine
from .routes import patient
from .core.config import get_settings
Base.metadata.create_all(bind=engine)
settings = get_settings()
app = FastAPI(title=settings.PROJECT_NAME)

@app.get("/health")
def health(): return {"status": "ok", "service": "patient-service"}

app.include_router(patient.router)