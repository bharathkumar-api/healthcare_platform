from fastapi import FastAPI
app = FastAPI(title="Healthcare - Billing Service")

@app.get("/health")
def health(): return {"status":"ok","service":"billing-service"}