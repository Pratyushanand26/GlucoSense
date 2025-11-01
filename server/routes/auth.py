from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    message: str
    token: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # Mock authentication logic
    if request.email == "test@example.com" and request.password == "password":
        return LoginResponse(message="Login successful", token="mock-token")
    raise HTTPException(status_code=401, detail="Invalid credentials")