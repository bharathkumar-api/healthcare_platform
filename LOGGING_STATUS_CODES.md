# HTTP Status & Logging Playbook

This repository runs multiple FastAPI microservices (auth, gateway, patient, provider, appointment, billing, notification).  
Each service must emit consistent status codes and structured logs so we can trace issues end‑to‑end.

## 1. Critical HTTP Status Codes to Track

| Class | Code | When to return | What to log |
| --- | --- | --- | --- |
| 200 | Successful GET/PUT where a body is returned | latency, tenant/user id, payload size |
| 201 | Resource creation (`POST /patients`, `/appointments`, `/auth/register`) | DB insert timing, generated id |
| 202 | Async workflows (notifications, background jobs) | queue name, job id, ETA |
| 204 | Successful DELETE/empty response | affected rows |
| 400 | Bad payload/schema mismatch | validation error, field list |
| 401 | Auth failure/token issues | auth header hash, issuer |
| 403 | RBAC denied | role/permission tested |
| 404 | Missing resource (`/patients/me` before profile exists) | lookup keys |
| 409 | Conflict/idempotency failures | conflicting id, current state |
| 422 | Business validation errors | domain rule name |
| 429 | Rate limiting | limiter key, retry-after |
| 500 | Unhandled exception | stack trace id |
| 502 | Upstream dependency error | upstream host, status |
| 503 | Service unavailable (DB down, circuit open) | dependency health reason |
| 504 | Gateway timeout | timeout threshold exceeded |

A spike in slow 200s should page the team—they often precede 5xx.

## 2. Structured Logging Contract

Emit JSON per request with the following keys:

```
{
  "timestamp": "...",
  "service": "patient-service",
  "method": "GET",
  "path": "/api/v1/patients/me",
  "status": 404,
  "duration_ms": 21.7,
  "correlation_id": "...",
  "user_id": "...",
  "client_ip": "...",
  "error": "Patient profile not found"
}
```

### FastAPI Middleware Snippet

Add to each service’s `main.py`:

```python
import time, logging
from fastapi import Request
from uuid import uuid4

logger = logging.getLogger("service")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    correlation_id = request.headers.get("x-correlation-id", str(uuid4()))
    try:
        response = await call_next(request)
    except Exception as exc:
        duration = (time.perf_counter() - start) * 1000
        logger.exception({
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id,
            "service": SERVICE_NAME,
            "method": request.method,
            "path": request.url.path,
            "status": 500,
            "duration_ms": duration
        })
        raise

    duration = (time.perf_counter() - start) * 1000
    logger.info({
        "timestamp": datetime.utcnow().isoformat(),
        "correlation_id": correlation_id,
        "service": SERVICE_NAME,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": duration
    })
    response.headers["x-correlation-id"] = correlation_id
    return response
```

### Log Levels
- INFO: 2xx/3xx + validation errors (4xx) that are expected.
- WARNING: Repeated 4xx from same user, 409 conflicts.
- ERROR: 5xx, failed downstream calls.
- CRITICAL: Dependency outages (DB down, queue unavailable).

## 3. Service-Specific Notes

| Service | Entry file | Key endpoints | Notes |
| --- | --- | --- | --- |
| gateway-service | `src/main.py` | `/api/v1/* proxy` | gate all requests, append upstream status |
| auth-service | `src/main.py` | `/api/v1/auth/login`, `/register`, `/me` | mask credentials in logs |
| patient-service | `src/main.py` | `/api/v1/patients`, `/me` | log 404 when profile missing |
| provider-service | `src/main.py` | `/api/v1/providers` | capture query params (specialty) |
| appointment-service | `src/main.py` | `/api/v1/appointments` | include patient/provider ids |
| billing-service | `src/main.py` | `/api/v1/billing` | log payment gateway responses |
| notification-service | `src/main.py` | `/api/v1/notifications` | pair 202 with queue message id |

## 4. Metrics to Capture

- **Latency percentiles** per route (`p50`, `p95`, `p99`).
- **Response size** histogram (watch for large 200s).
- **Error rate** broken down by status class (4xx vs 5xx).
- **Correlation tracing**: propagate `x-correlation-id` between gateway → downstream.

Recommended Prometheus labels: `service`, `status_code`, `method`, `route`, `success`.

## 5. Alerting Ideas

1. `5xx_rate > 2%` for 5 minutes per service.
2. `latency_p95 > 1s` for GETs.
3. `429 spikes` → throttle tuning.
4. `High 204 + low DB writes` → detect silent delete failures.

## 6. Rollout Checklist

1. Add middleware snippet to each FastAPI service.
2. Ensure gunicorn/uvicorn streams JSON (set `log_config`).
3. Ship logs to ELK/Datadog using Docker logging driver.
4. Configure dashboard panels per code class.
5. Simulate 404/500 scenarios to verify structured output.

Use this doc when instrumenting new endpoints to keep consistency across the platform.
