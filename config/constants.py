# Constants for the Healthcare Platform

BASE_URL = "https://api.healthcareplatform.com"
JWT_SECRET = "your_jwt_secret_key"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# User roles
ROLE_ADMIN = "admin"
ROLE_PROVIDER = "provider"
ROLE_PATIENT = "patient"

# Notification settings
EMAIL_NOTIFICATION_ENABLED = True
SMS_NOTIFICATION_ENABLED = True

# Database settings
DATABASE_URL = "postgresql://user:password@localhost:5432/healthcare_db"
DATABASE_TIMEOUT = 30

# Other constants
DEFAULT_LANGUAGE = "en"
MAX_PATIENTS_PER_PROVIDER = 1000