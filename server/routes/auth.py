"""Authentication routes"""
import uuid
from fastapi import APIRouter, HTTPException
from ..models import SignUpRequest, SignUpResponse, LoginRequest, LoginResponse
from ..auth import get_password_hash, verify_password
from ..database import users_collection

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/signup", response_model=SignUpResponse)
async def signup_user(request: SignUpRequest):
    """Register new patient"""
    existing = await users_collection.find_one({"email": request.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = get_password_hash(request.password)
    user_id = str(uuid.uuid4())
    
    user_doc = {
        "_id": user_id,
        "email": request.email,
        "hashed_password": hashed_pwd,
        "role": "patient",
        "age": request.age,
        "height_cm": request.height_cm,
        "sex": request.sex,
        "medical_history": request.medical_history.dict(),
        "family_history": request.family_history.dict(),
        "lifestyle_factors": request.lifestyle_factors.dict(),
        "body_weight_kg": None
    }
    
    await users_collection.insert_one(user_doc)
    print(f"[AUTH] New patient: {request.email}")
    
    return SignUpResponse(message="User signed up successfully", user_id=user_id)

@router.post("/login", response_model=LoginResponse)
async def login_user(request: LoginRequest):
    """Login and get token"""
    print(f"[AUTH] Login: {request.email}")
    
    # Doctor login
    if request.email == "doctor@example.com" and request.password == "doctorpass":
        return LoginResponse(
            message="Doctor logged in",
            token="fake-token::doc-123::doctor",
            role="doctor"
        )
    
    # Patient login
    user = await users_collection.find_one({"email": request.email})
    if user and verify_password(request.password, user["hashed_password"]):
        if user["role"] == "patient":
            return LoginResponse(
                message="Patient logged in",
                token=f"fake-token::{user['_id']}::patient",
                role="patient"
            )
    
    raise HTTPException(status_code=401, detail="Invalid credentials")