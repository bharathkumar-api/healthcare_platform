#!/bin/bash

# This script sets up the healthcare platform environment.

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install necessary packages
echo "Installing necessary packages..."
sudo apt-get install -y python3 python3-pip docker-compose

# Set up Python virtual environments for each service
echo "Setting up Python virtual environments for services..."
for service in auth-service patient-service provider-service appointment-service billing-service notification-service gateway-service; do
    cd $service
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    cd ..
done

# Start Docker containers
echo "Starting Docker containers..."
docker-compose up -d

echo "Setup completed successfully!"