from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from ..schemas import User, UserCreate, Token, LoginRequest
from ..models import User as UserModel
from ..core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from ..core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from ..database import get_db

router = APIRouter()

# Change this to HTTPBearer for simple token authentication in Swagger
security = HTTPBearer()

def get_user_by_username(db: Session, username: str):
    """Get user by username"""
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(UserModel).filter(UserModel.email == email).first()

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user with username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username already exists
    existing_user = get_user_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered. Please choose a different username."
        )
    
    # Check if email already exists
    existing_email = get_user_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please use a different email or login."
        )
    
    # Create new user
    try:
        hashed_password = get_password_hash(user_in.password)
        db_user = UserModel(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            role=user_in.role if hasattr(user_in, 'role') else 'patient'
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from ..schemas import User, UserCreate, Token, LoginRequest
from ..models import User as UserModel
from ..core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from ..core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from ..database import get_db

router = APIRouter()

# Change this to HTTPBearer for simple token authentication in Swagger
security = HTTPBearer()

def get_user_by_username(db: Session, username: str):
    """Get user by username"""
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_user_by_email(db: Session, email: str):
    """Get user by email"""
    return db.query(UserModel).filter(UserModel.email == email).first()

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user with username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username already exists
    existing_user = get_user_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered. Please choose a different username."
        )
    
    # Check if email already exists
    existing_email = get_user_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please use a different email or login."
        )
    
    # Create new user
    try:
        hashed_password = get_password_hash(user_in.password)
        db_user = UserModel(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            role=user_in.role if hasattr(user_in, 'role') else 'patient'
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with username and password"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user from Bearer token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username = payload.get("sub")
    user_id = payload.get("user_id")
    
    if username is None or user_id is None:
        raise credentials_exception
    
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    
    return {"username": user.username, "user_id": user.id, "role": user.role}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user from Bearer token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username = payload.get("sub")
    user_id = payload.get("user_id")
    
    if username is None or user_id is None:
        raise credentials_exception
    
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    
    return {"username": user.username, "user_id": user.id, "role": user.role}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user