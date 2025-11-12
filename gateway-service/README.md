# Gateway Service

This directory contains the implementation of the Gateway Service for the Healthcare Platform. The Gateway Service acts as an API gateway, routing requests to the appropriate microservices and handling cross-cutting concerns such as authentication and logging.

## Structure

- `src/main.py`: The entry point for the FastAPI application, where routes and middleware are defined.
- `requirements.txt`: Lists the dependencies required for the Gateway Service.

## Getting Started

To run the Gateway Service, ensure you have Python 3.7+ installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

You can start the service by running:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

The Gateway Service provides endpoints to interact with the various microservices in the healthcare platform. Refer to the documentation of each respective service for details on the available endpoints.

## Contributing

Contributions are welcome! Please follow the standard contribution guidelines for this project.