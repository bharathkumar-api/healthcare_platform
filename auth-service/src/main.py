from fastapi import FastAPI
from .database import Base, engine
from .routes import auth as auth_routes
from .core.config import get_settings

settings = get_settings()

# Create tables on startup (OK for dev; later use Alembic for prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": "auth-service"}


app.include_router(auth_routes.router) 

