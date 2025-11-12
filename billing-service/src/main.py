from fastapi import FastAPI
app = FastAPI(title="Healthcare - Billing Service")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health(): return {"status":"ok","service":"billing-service"}

