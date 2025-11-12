# Auth Service

FastAPI-based authentication service for the Healthcare Platform.

## Features

- User registration (patient/doctor/admin)
- Login with email + password
- JWT access tokens
- `/auth/me` endpoint to fetch current user
- `/health` for liveness checks

## Local Run

```bash
cd auth-service
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
export DB_USER=postgres DB_PASSWORD=postgres DB_HOST=localhost DB_NAME=healthcare_auth
export JWT_SECRET_KEY="CHANGE_ME"
uvicorn src.main:app --reload