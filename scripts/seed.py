import os
import json

def seed_data():
    # Example seed data for different services
    patients = [
        {"id": 1, "name": "John Doe", "age": 30, "medical_history": []},
        {"id": 2, "name": "Jane Smith", "age": 25, "medical_history": []}
    ]

    providers = [
        {"id": 1, "name": "Dr. Alice", "specialty": "Cardiology"},
        {"id": 2, "name": "Dr. Bob", "specialty": "Dermatology"}
    ]

    appointments = [
        {"id": 1, "patient_id": 1, "provider_id": 1, "date": "2023-10-01", "time": "10:00"},
        {"id": 2, "patient_id": 2, "provider_id": 2, "date": "2023-10-02", "time": "11:00"}
    ]

    # Define the path to the seed files
    seed_files = {
        "patients.json": patients,
        "providers.json": providers,
        "appointments.json": appointments
    }

    # Create a directory for seed data if it doesn't exist
    os.makedirs('seed_data', exist_ok=True)

    # Write seed data to JSON files
    for filename, data in seed_files.items():
        with open(os.path.join('seed_data', filename), 'w') as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    seed_data()