import uvicorn
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field, conint
from typing import List, Optional
from datetime import date
import uuid

app = FastAPI(
    title="Main Application API",
    description="API for user auth, profile, and daily check-ins.",
    version="1.0.0"
)

# --- Auth and User Input Models ---
# These models define the data structure for your new endpoints.

class SignUpRequest(BaseModel):
    """Data model for the signup request."""
    email: str
    password: str # In a real app, this would be hashed
    pre_existing_conditions: Optional[List[str]] = Field(None, example=["Hypertension", "Type 2 Diabetes"])
    general_notes: Optional[str] = Field(None, example="Was a smoker for 5 years.")

class SignUpResponse(BaseModel):
    """Data model for the signup response."""
    message: str
    user_id: str

class LoginRequest(BaseModel):
    """Data model for the login request."""
    email: str
    password: str

class LoginResponse(BaseModel):
    """Data model for the login response."""
    message: str
    token: str # A mock JWT (JSON Web Token)

class UserProfile(BaseModel):
    """
    Data model for 'static' user info.
    All fields are optional, so the user can update one at a time.
    """
    age: Optional[int] = Field(None, example=30)
    height_cm: Optional[float] = Field(None, example=175.5)
    weight_kg: Optional[float] = Field(None, example=78.0)

class IllnessReport(BaseModel):
    """A sub-model to cleanly handle illness reporting."""
    has_symptoms: bool = Field(..., example=True)
    description: Optional[str] = Field(None, example="Sore throat and cough.")
    duration_days: Optional[int] = Field(None, example=2)

class DailyCheckIn(BaseModel):
    """
    Data model for the user's daily check-in.
    We use 'conint' to enforce the 0-10 range.
    """
    illness_symptoms: Optional[IllnessReport] = None
    energy_level: conint(ge=0, le=10) = Field(..., example=7)
    muscle_soreness: conint(ge=0, le=10) = Field(..., example=3)
    mood_state: conint(ge=0, le=10) = Field(..., example=8)
    additional_info: Optional[str] = Field(None, example="Had a very stressful meeting today.")


# --- Auth Endpoints (Mocked) ---
# These endpoints simulate user signup and login.

@app.post(
    "/api/v1/auth/signup",
    response_model=SignUpResponse,
    summary="User Sign-up",
    description="Registers a new user. Mocks database creation."
)
def signup_user(request: SignUpRequest):
    """
    Mocks a user signup.
    In a real app, you would hash the password and save to a database.
    Here, we just print the data and return a success message.
    """
    print(f"[AUTH] Received new signup for email: {request.email}")
    print(f"[AUTH] Pre-existing conditions: {request.pre_existing_conditions}")
    
    # Mock a new user ID
    new_user_id = str(uuid.uuid4())
    
    return SignUpResponse(
        message="User signed up successfully (mocked).",
        user_id=new_user_id
    )

@app.post(
    "/api/v1/auth/login",
    response_model=LoginResponse,
    summary="User Login",
    description="Logs in a user. Mocks token generation."
)
def login_user(request: LoginRequest):
    """
    Mocks a user login.
    In a real app, you'd verify credentials and generate a real JWT.
    Here, we just return a fake token.
    """
    print(f"[AUTH] Received login attempt for: {request.email}")
    
    # Mock a JWT token
    mock_token = f"fake-jwt-token-for-{request.email}-{str(uuid.uuid4())[:8]}"
    
    return LoginResponse(
        message="User logged in successfully (mocked).",
        token=mock_token
    )

# --- User Data Input Endpoints ---
# These endpoints are for the user to submit their own data.

@app.put(
    "/api/v1/user/profile",
    response_model=UserProfile,
    summary="Update User Profile",
    description="Sets or updates 'static' user data like age, height, and weight."
)
def update_user_profile(profile_data: UserProfile):
    """
    Mocks saving user profile data.
    Using PUT means this endpoint is for creating or replacing the profile.
    Since all fields are Optional, the frontend can send only what it needs.
    """
    print(f"[PROFILE] Received profile update: {profile_data.dict(exclude_unset=True)}")
    # In a real app, you'd fetch the user from the DB and update their fields.
    
    return profile_data # Return the data we received as confirmation

@app.post(
    "/api/v1/user/checkin",
    summary="Submit Daily Check-in",
    description="Endpoint for the user to log their daily metrics and feelings."
)
def submit_daily_checkin(checkin_data: DailyCheckIn):
    """
    Mocks saving a new daily check-in to the database.
    Using POST because each check-in is a new, separate entry.
    """
    print(f"[CHECK-IN] Received new daily check-in:")
    print(checkin_data.dict())
    
    return {
        "message": "Daily check-in received successfully (mocked).",
        "checkin_date": date.today(),
        "received_data": checkin_data
    }

# --- Server Runner ---

if __name__ == "__main__":
    """
    This allows you to run the server directly by running
    `python main.py` in your terminal.
    """
    print("Starting Main App FastAPI server at http://127.0.0.1:8000")
    print("View API docs at http://127.0.0.1:8000/docs")
    print("---")
    print("App Endpoints (POST/PUT):")
    print("  http://127.0.0.1:8000/api/v1/auth/signup (POST)")
    print("  http://127.0.0.1:8000/api/v1/auth/login (POST)")
    print("  http://127.0.0.1:8000/api/v1/user/profile (PUT)")
    print("  http://127.0.0.1:8000/api/v1/user/checkin (POST)")
    uvicorn.run(app, host="127.0.0.1", port=8000)

