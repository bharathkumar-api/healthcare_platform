from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import auth

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Healthcare Platform - Auth Service",
    description="Authentication and Authorization Service",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "auth-service"}