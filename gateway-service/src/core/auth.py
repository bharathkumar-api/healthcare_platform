from fastapi import HTTPException, status
from jose import jwt, JWTError
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-min-32-chars-long-change-in-production!!")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def validate_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        username = payload.get("username")
        role = payload.get("role", "patient")
        
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        # Accept both string and integer user_id
        if isinstance(user_id, str):
            try:
                user_id = int(user_id)
            except ValueError:
                pass
        
        return {"user_id": user_id, "username": username, "role": role}
    except JWTError as e:
        print(f"JWT validation failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials: {str(e)}")
