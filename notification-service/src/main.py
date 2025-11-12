from fastapi import FastAPI
app = FastAPI(title="Healthcare - Notification Service")

@app.get("/health")
def health(): return {"status":"ok","service":"notification-service"}