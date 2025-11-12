from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Healthcare Platform API Gateway"}

# Additional routes can be added here for different services
# Example: 
# @app.get("/patients")
# def get_patients():
#     return {"patients": []}  # Replace with actual logic to fetch patients

# More routes can be defined for other services like auth, appointments, etc.