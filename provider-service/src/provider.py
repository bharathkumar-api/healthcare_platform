from fastapi import APIRouter, HTTPException
from .models import Provider, ProviderIn

router = APIRouter()

# In-memory storage for providers (for demonstration purposes)
providers_db = {}

@router.post("/providers/", response_model=Provider)
def create_provider(provider: ProviderIn):
    provider_id = len(providers_db) + 1
    provider_data = provider.dict()
    provider_data["id"] = provider_id
    providers_db[provider_id] = provider_data
    return provider_data

@router.get("/providers/{provider_id}", response_model=Provider)
def read_provider(provider_id: int):
    provider = providers_db.get(provider_id)
    if provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider

@router.get("/providers/", response_model=list[Provider])
def read_providers():
    return list(providers_db.values())

@router.put("/providers/{provider_id}", response_model=Provider)
def update_provider(provider_id: int, provider: ProviderIn):
    if provider_id not in providers_db:
        raise HTTPException(status_code=404, detail="Provider not found")
    provider_data = provider.dict()
    provider_data["id"] = provider_id
    providers_db[provider_id] = provider_data
    return provider_data

@router.delete("/providers/{provider_id}", response_model=dict)
def delete_provider(provider_id: int):
    if provider_id not in providers_db:
        raise HTTPException(status_code=404, detail="Provider not found")
    del providers_db[provider_id]
    return {"detail": "Provider deleted"}