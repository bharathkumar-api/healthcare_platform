from fastapi import FastAPI
app = FastAPI(title="Healthcare - API Gateway (placeholder)")
@app.get("/health")
def health(): return {"status":"ok","service":"gateway-service"}