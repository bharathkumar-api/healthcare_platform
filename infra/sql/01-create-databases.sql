-- Create all databases for healthcare platform microservices
CREATE DATABASE healthcare_auth;
CREATE DATABASE healthcare_patient;
CREATE DATABASE healthcare_appointment;
CREATE DATABASE healthcare_billing;

-- Grant all privileges to postgres user
GRANT ALL PRIVILEGES ON DATABASE healthcare_auth TO postgres;
GRANT ALL PRIVILEGES ON DATABASE healthcare_patient TO postgres;
GRANT ALL PRIVILEGES ON DATABASE healthcare_appointment TO postgres;
GRANT ALL PRIVILEGES ON DATABASE healthcare_billing TO postgres;
