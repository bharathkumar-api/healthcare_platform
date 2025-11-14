# filepath: /Users/bharathkumarveeramalli/healthcare_platform-2/provider-service/src/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.database.session import engine
from src.models import provider
from src.database.seed import seed_providers
from src.database.session import get_db
import logging
import json
import time
from uuid import uuid4
from datetime import datetime

SERVICE_NAME = "provider-service"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(SERVICE_NAME)

# Create tables
provider.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Healthcare Provider Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Structured logging for provider endpoints."""
    start = time.perf_counter()
    correlation_id = request.headers.get("x-correlation-id", str(uuid4()))
    request.state.correlation_id = correlation_id

    try:
        response = await call_next(request)
    except Exception as exc:
        duration = (time.perf_counter() - start) * 1000
        error_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": SERVICE_NAME,
            "method": request.method,
            "path": request.url.path,
            "status": 500,
            "duration_ms": round(duration, 2),
            "correlation_id": correlation_id,
            "error": str(exc)
        }
        logger.exception(json.dumps(error_entry))
        raise

    duration = (time.perf_counter() - start) * 1000
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": SERVICE_NAME,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round(duration, 2),
        "correlation_id": correlation_id
    }

    if response.status_code >= 500:
        logger.error(json.dumps(log_entry))
    elif response.status_code >= 400:
        logger.warning(json.dumps(log_entry))
    else:
        logger.info(json.dumps(log_entry))

    response.headers["X-Correlation-ID"] = correlation_id
    return response

# Include routes
app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Seed database on startup"""
    logger.info("🚀 Starting Provider Service...")
    try:
        db = next(get_db())
        seed_providers(db)
        logger.info("✅ Provider Service ready!")
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "provider-service",
        "version": "1.0.0"
    }
