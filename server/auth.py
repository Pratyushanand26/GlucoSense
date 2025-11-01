# Authentication logic
"""Authentication utilities"""
from typing import Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from .database import users_collection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
token_auth_scheme = HTTPBearer()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(token_auth_scheme)) -> Dict:
    """Validate token and get user info"""
    try:
        parts = token.credentials.split("::")
        if len(parts) != 3:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        user_id, role = parts[1], parts[2]
        
        # Special doctor account
        if user_id == "doc-123" and role == "doctor":
            return {"user_id": user_id, "role": role}
        
        # Patient account
        user = await users_collection.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
        
        user_role = user.get("role", "patient")
        if user_role != role:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Role mismatch")
        
        return {"user_id": user_id, "role": role}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

async def get_patient_user(current_user: Dict = Depends(get_current_user)) -> str:
    """Ensure user is a patient"""
    if current_user["role"] != "patient":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires patient role")
    return current_user["user_id"]

async def get_doctor_user(current_user: Dict = Depends(get_current_user)) -> str:
    """Ensure user is a doctor"""
    if current_user["role"] != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires doctor role")
    return current_user["user_id"]