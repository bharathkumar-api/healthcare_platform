# Healthcare Platform

This project is a comprehensive healthcare platform designed to manage various aspects of healthcare services, including patient information, provider data, appointment scheduling, billing, and notifications. The architecture is microservices-based, allowing for scalability and maintainability.

## Project Structure

The project is organized into several services, each responsible for a specific domain:

- **infra/**: Contains Docker Compose files, CI/CD configurations, and shared environment settings.
- **gateway-service/**: Acts as the API gateway, built using FastAPI or Traefik, routing requests to the appropriate services.
- **auth-service/**: Manages authentication and authorization using JWT and OAuth2, handling user roles.
- **patient-service/**: Responsible for managing patient information and medical history.
- **provider-service/**: Contains data related to healthcare providers, including specialties.
- **appointment-service/**: Manages appointment scheduling and reminders for patients and providers.
- **billing-service/**: Handles billing operations, including insurance claims, payments, and invoices.
- **notification-service/**: Sends email and SMS alerts for various events within the platform.
- **ui-service/**: A React application that serves as the frontend for the healthcare platform.

## Getting Started

To get started with the healthcare platform, follow these steps:

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd healthcare_platform
   ```

2. **Set up the environment**:
   - Ensure you have Docker and Docker Compose installed.
   - Configure environment variables as needed.

3. **Build and run the services**:
   ```
   docker-compose up --build
   ```

4. **Access the application**:
   - The API gateway will be available at `http://localhost:8000`.
   - The UI service can be accessed at `http://localhost:3000`.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.