import uvicorn
import os
import random
import uuid
import httpx  # For making API calls
import json   # For formatting data for the agent
from datetime import date, timedelta
from typing import List, Optional, Dict
from dotenv import load_dotenv

from fastapi import FastAPI, Body, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, conint, EmailStr
from passlib.context import CryptContext
import motor.motor_asyncio
from bson import ObjectId

# --- 0. Import your AI model ---
# (I've placed your model code here)
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

# --- 1. Load Environment Variables & Config ---
load_dotenv()  # Loads variables from .env file

# --- Security & Password Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
token_auth_scheme = HTTPBearer()

# --- Mock Server URL ---
# This is the address of your *other* server (mock_server.py)
# It runs on port 8001
MOCK_SERVER_URL = "http://127.0.0.1:8001/api/v1/health/weekly-summary"

# --- Gemini API Key ---
GEMINI_API_KEY ="AIzaSyBqYJqqT33hQuwmWZWCzOtDrjUpqYgrSbQ"
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in .env file. 'evaluate' will fail.")
else:
    genai.configure(api_key=GEMINI_API_KEY)


# --- FastAPI App Initialization ---
app = FastAPI(
    title="Main Application API",
    description="API for user auth, profile, daily check-ins, and doctor analysis.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. Database Connection ---
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
if not MONGO_CONNECTION_STRING:
    raise RuntimeError("FATAL ERROR: MONGO_CONNECTION_STRING not found in .env file")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_CONNECTION_STRING)
db = client.get_database("healthAppDb")
users_collection = db.get_collection("users")
records_collection = db.get_collection("daily_records")

# --- 3. Pydantic Models (Data Schemas) ---

# --- Baseline Profile (from Signup) ---
class MedicalHistory(BaseModel):
    chronic_conditions: List[str] = Field(default_factory=list, example=["Diabetes Type 2", "Hypertension"])
    past_surgeries: List[str] = Field(default_factory=list, example=["Appendectomy"])
    current_medications: List[str] = Field(default_factory=list, example=["Metformin 500mg"])
    known_allergies: List[str] = Field(default_factory=list, example=["Pollen"])

class FamilyHistory(BaseModel):
    heart_disease: bool = Field(False)
    diabetes: bool = Field(False)
    cancer: bool = Field(False)
    other_hereditary_conditions: List[str] = Field(default_factory=list)

class LifestyleFactors(BaseModel):
    smoking_status: str = Field(..., example="Never Smoked")
    alcohol_consumption: str = Field(..., example="Occasionally")
    exercise_habits: str = Field(..., example="3-4 times a week")

class SignUpRequest(BaseModel):
    """Data model for the signup request, including the baseline profile."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    age: int = Field(..., example=35)
    height_cm: float = Field(..., example=180.3)
    sex: str = Field(..., example="Male")
    medical_history: MedicalHistory
    family_history: FamilyHistory
    lifestyle_factors: LifestyleFactors

class SignUpResponse(BaseModel):
    message: str
    user_id: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    message: str
    token: str
    role: str

# --- User Profile (Stored in 'users' collection) ---
class UserProfile(BaseModel):
    """
    Data model for 'static' user info stored in the 'users' collection.
    """
    id: str = Field(..., alias="_id")
    email: EmailStr
    age: int
    height_cm: float
    sex: str
    body_weight_kg: Optional[float] = Field(None, example=80.5)
    medical_history: MedicalHistory
    family_history: FamilyHistory
    lifestyle_factors: LifestyleFactors

class UserInDB(UserProfile):
    """Model for the full user document in the database, including hashed_password."""
    hashed_password: str

# --- Daily Check-in & Device Data ---
# These models MUST match the ones in mock_server.py
class HeartRate(BaseModel):
    resting_hr: int
    average_weekly_hr: int

class HRV(BaseModel):
    average_hrv: int

class Sleep(BaseModel):
    sleep_duration_hours: float

class PhysicalActivity(BaseModel):
    steps: int
    calories_burned: int

class SpO2(BaseModel):
    average_spo2: float

class SkinTemperature(BaseModel):
    deviation_celsius: float

class WeeklyMetric(BaseModel):
    """This is the response model from mock_server.py"""
    date: date
    heart_rate: HeartRate
    hrv: HRV
    sleep: Sleep
    activity: PhysicalActivity
    spo2: SpO2
    skin_temp: SkinTemperature

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class IllnessReport(BaseModel):
    present: bool = Field(..., example=True)
    description: Optional[str] = Field(None, example="Sore throat and cough.")
    duration_days: Optional[int] = Field(None, example=2)

class DailyCheckIn(BaseModel):
    """Data model for the user's daily check-in (what the user submits)."""
    body_weight_kg: float = Field(..., example=80.2)
    illness_symptoms: IllnessReport
    energy_level: conint(ge=0, le=10) = Field(..., example=7)
    muscle_soreness: conint(ge=0, le=10) = Field(..., example=3)
    mood_state: conint(ge=0, le=10) = Field(..., example=8)
    location_coordinates: Optional[Coordinates] = None
    additional_notes: Optional[str] = Field(None, example="Had a very stressful meeting today.")

class MergedDailyRecord(BaseModel):
    """
    The final, combined record to be stored in the 'daily_records' collection.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    date: date
    
    # From DailyCheckIn
    checkin_data: DailyCheckIn
    
    # From mock_server.py
    device_data: WeeklyMetric

# --- Agent Analysis Models ---
class AgentAnalysisInput(BaseModel):
    baseline_profile: UserProfile
    daily_records: List[MergedDailyRecord]

class AgentAnalysisResponse(BaseModel):
    """
    The response from the /analyze endpoint.
    It returns the raw text from the Gemini model.
    """
    patient_id: str
    analysis_text: str

# --- 4. Helper Functions (Password) ---
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- 5. Authentication & Role Dependencies ---
async def get_current_user(token: HTTPAuthorizationCredentials = Depends(token_auth_scheme)) -> Dict:
    """
    Dependency to "validate" a token and get user info.
    This is a MOCK function.
    """
    try:
        # Real app: decode JWT. Here: parse "fake-token::{user_id}::{role}"
        parts = token.credentials.split("::")
        if len(parts) != 3:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")
        
        user_id, role = parts[1], parts[2]
        
        user = None
        if user_id == "doc-123" and role == "doctor":
            user = {"_id": user_id, "role": role} # Mock doctor user
        else:
            # FIXED: Just query directly with the string user_id
            # No need to validate as ObjectId since we're using UUIDs
            user = await users_collection.find_one({"_id": user_id})

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")
        
        user_role = user.get("role", "patient")
        if user_role != role:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token role mismatch")

        return {"user_id": user_id, "role": role}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_patient_user(current_user: Dict = Depends(get_current_user)) -> str:
    """Dependency to ensure the user is a 'patient'."""
    if current_user["role"] != "patient":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires patient role")
    return current_user["user_id"]

async def get_doctor_user(current_user: Dict = Depends(get_current_user)) -> str:
    """Dependency to ensure the user is a 'doctor'."""
    if current_user["role"] != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires doctor role")
    return current_user["user_id"]

# --- 6. Core Logic Functions ---

async def create_daily_record(user_id: str, checkin_data: DailyCheckIn, device_data: WeeklyMetric) -> MergedDailyRecord:
    """
    NEW NAME: This was 'databasemock'.
    Merges check-in and device data and saves it to the 'daily_records' collection.
    """
    from datetime import datetime  # Add this import at the top if not already there
    
    print(f"[create_daily_record] Merging data for user {user_id}")
    
    # Create the final, merged record
    merged_record = MergedDailyRecord(
        _id=str(uuid.uuid4()),
        user_id=user_id,
        date=date.today(),
        checkin_data=checkin_data,
        device_data=device_data
    )
    
    # Convert to dict and fix date fields for MongoDB
    record_dict = merged_record.dict(by_alias=True)
    
    # Convert date objects to datetime objects for MongoDB
    if isinstance(record_dict['date'], date):
        record_dict['date'] = datetime.combine(record_dict['date'], datetime.min.time())
    
    if isinstance(record_dict['device_data']['date'], date):
        record_dict['device_data']['date'] = datetime.combine(record_dict['device_data']['date'], datetime.min.time())
    
    await records_collection.insert_one(record_dict)
    print(f"[create_daily_record] Saved new record {merged_record.id} for user {user_id}")
    return merged_record
#
# --- YOUR EVALUATE FUNCTION ---
#
def evaluate(data: str) -> str:
    """
    NEW NAME: This was 'agentmock'.
    Calls the Gemini API with the provided data and prompt.
    """
    print('evaluating...')
    if not GEMINI_API_KEY:
        print("ERROR: Cannot evaluate. GEMINI_API_KEY is not set.")
        return "Error: AI model is not configured."
    
    try:
        # Initialize client here to ensure it uses the configured API key
        client = genai.GenerativeModel(model_name="gemini-2.5-pro")
        
        # This is the prompt from your code
        Instruction = """
        # ENHANCED HEALTH DATA EVALUATION SYSTEM PROMPT

        ROLE: You are an AI health analyst combining medical knowledge and statistical expertise 
        to evaluate personal health data and provide actionable insights.

        === INPUT DATA STRUCTURE ===
        (It will be a JSON string of baseline_profile and daily_records)

        === EVALUATION METHODOLOGY ===
        1. TREND ANALYSIS:
        - Compare current week vs. previous 4-8 weeks
        - Identify significant deviations (>15-20% change in key metrics)
        - Detect concerning patterns (consistent decline/increase)

        2. CORRELATION ASSESSMENT:
        - Cross-reference multiple declining metrics simultaneously
        - Consider seasonal/environmental factors (location, weather)
        - Account for expected variations (age, activity level changes)

        3. RED FLAGS TO PRIORITIZE:
        - Resting heart rate: >100 bpm or <40 bpm (unless athlete)
        - SpO₂: <92% (sustained)
        - Unexplained weight loss: >5% in 4 weeks
        - Persistent symptoms: Illness >7 days without improvement
        - Heart rate variability: Sudden drop >30% sustained for 2+ weeks
        - Sleep duration: <4 hours or >12 hours consistently
        - Combined warning signs: Multiple metrics declining together

        4. CONTEXT CONSIDERATION:
        - Recent illness recovery periods (expect temporary metric changes)
        - Travel/location changes (jet lag, altitude)
        - Known medication side effects
        - Age-appropriate baselines
        - Pre-existing conditions

        === OUTPUT FORMAT ===

        *STATUS: [NORMAL / CONSULT RECOMMENDED]*

        ---

        *HEALTH CHECK SUMMARY*

        Evaluation Period: [Date Range]

        *Current Status:* [One-line friendly summary]

        *What We're Seeing:*
        [2-3 paragraphs in plain language explaining:
        - Overall health trends in accessible terms
        - Any changes noticed compared to recent weeks
        - Context for why certain changes might be happening]

        *Key Observations:*

        ✓ *Going Well:*
        - [Positive findings in friendly language]
        - [Metrics within healthy range]

        ⚠ *Worth Noting:*
        - [Areas showing changes but not urgent]
        - [Suggestions for self-monitoring]

        [IF APPLICABLE]
        🔴 *Needs Attention:*
        - [Specific concerns requiring medical consultation]
        - [Why this matters for your health]

        *Recommendations:*

        Immediate Actions (No Risk):
        [3-5 lifestyle suggestions anyone can safely try:
        - Sleep: "Aim for [X] hours tonight - your body uses sleep to recover"
        - Hydration: "Try drinking [X] glasses of water throughout the day"
        - Movement: "A 10-minute walk after meals can help with [specific benefit]"
        - Stress: "Take 5 deep breaths when you feel tension building"
        - Rest: "Take short breaks every hour if you're feeling fatigued"]

        Monitoring & Follow-up:
        [Specific tracking recommendations:
        1. Continue monitoring [specific metric] for another week
        2. Keep notes on [symptom/pattern] to discuss with your doctor
        3. Track how you feel after implementing the lifestyle changes above]

        Professional Consultation:
        [If applicable - when medical advice is recommended:
        - Schedule a routine checkup to discuss [specific concern]
        - Contact your doctor if [specific symptom] continues beyond [timeframe]
        - Consider consulting about [specific pattern or metric]]

        *When to Seek Care:*
        [Clear, specific criteria for when to contact a healthcare provider]

        ---

        === COMMUNICATION GUIDELINES ===
        - Use conversational, reassuring language
        - Avoid medical jargon; explain any technical terms simply
        - Frame findings as "observations" not "diagnoses"
        - Be honest but not alarmist
        - Provide context for why metrics matter
        - Emphasize what the person CAN control
        - Include positive reinforcement where appropriate
        - Make recommendations specific and actionable
        - Clarify this is monitoring support, not medical diagnosis

        === CRITICAL SAFEGUARDS ===
        - NEVER diagnose specific medical conditions
        - ALWAYS recommend professional consultation for concerning patterns
        - NEVER suggest delaying care for serious symptoms
        - CLARIFY limitations: "This analysis helps track patterns but doesn't replace medical advice"
        - For emergencies (chest pain, difficulty breathing, severe symptoms): 
        Immediately recommend urgent medical care

        Now evaluate for this:
        :-{data}
        """
        
        # Combine the prompt and the data
        full_prompt = Instruction.format(data=data)

        # Call the API
        response = client.generate_content(full_prompt)

        print(response.text)
        return response.text
    
    except Exception as e:
        print(f"ERROR during Gemini evaluation: {e}")
        return f"Error: The AI analysis failed. Details: {e}"


# --- 7. Auth Endpoints (Public) ---

@app.post(
    "/api/v1/auth/signup",
    response_model=SignUpResponse,
    summary="User Sign-up",
    description="Registers a new user with their detailed baseline profile."
)
async def signup_user(request: SignUpRequest):
    """
    Saves a new user to the 'users' collection with a hashed password.
    """
    existing_user = await users_collection.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = get_password_hash(request.password)
    new_user_id = str(uuid.uuid4())
    
    user_document = {
        "_id": new_user_id,
        "email": request.email,
        "hashed_password": hashed_password,
        "role": "patient",
        "age": request.age,
        "height_cm": request.height_cm,
        "sex": request.sex,
        "medical_history": request.medical_history.dict(),
        "family_history": request.family_history.dict(),
        "lifestyle_factors": request.lifestyle_factors.dict(),
        "body_weight_kg": None
    }
    
    await users_collection.insert_one(user_document)
    print(f"[AUTH] New patient signup: {request.email} (ID: {new_user_id})")
    
    return SignUpResponse(
        message="User signed up successfully.",
        user_id=new_user_id
    )

@app.post(
    "/api/v1/auth/login",
    response_model=LoginResponse,
    summary="User Login"
)
async def login_user(request: LoginRequest):
    """
    Checks credentials and returns a fake role-based token.
    """
    print(f"[AUTH] Login attempt for: {request.email}")

    # --- Special Doctor Login ---
    if request.email == "doctor@example.com" and request.password == "doctorpass":
        return LoginResponse(
            message="Doctor logged in successfully.",
            token=f"fake-token::doc-123::doctor",
            role="doctor"
        )

    # --- Patient Login ---
    user = await users_collection.find_one({"email": request.email})
    
    if user and verify_password(request.password, user["hashed_password"]):
        if user["role"] == "patient":
            return LoginResponse(
                message="Patient logged in successfully.",
                token=f"fake-token::{user['_id']}::patient",
                role="patient"
            )

    raise HTTPException(status_code=401, detail="Invalid email or password")


# --- 8. Patient Endpoints (Requires 'patient' role) ---

@app.get(
    "/api/v1/user/profile",
    response_model=UserProfile,
    summary="Get User Profile"
)
async def get_user_profile(user_id: str = Depends(get_patient_user)):
    """
    Fetches the profile for the authenticated patient from 'users'.
    """
    profile = await users_collection.find_one({"_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.put(
    "/api/v1/user/profile",
    response_model=UserProfile,
    summary="Update User Profile"
)
async def update_user_profile(profile_data: UserProfile, user_id: str = Depends(get_patient_user)):
    """
    Updates the profile for the authenticated patient in 'users'.
    """
    if profile_data.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot update another user's profile")

    update_data = profile_data.dict(by_alias=False, exclude={"id"})
    
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )
    
    updated_profile = await users_collection.find_one({"_id": user_id})
    return updated_profile

@app.post(
    "/api/v1/user/checkin",
    response_model=MergedDailyRecord,
    summary="Submit Daily Check-in"
)
async def submit_daily_checkin(checkin_data: DailyCheckIn, user_id: str = Depends(get_patient_user)):
    """
    Saves a new daily record by:
    1. Getting patient's check-in data.
    2. Calling the mock device server (at MOCK_SERVER_URL).
    3. Calling `create_daily_record` to merge and save.
    4. Updating the main user profile's weight.
    """
    print(f"[CHECK-IN] Received check-in from patient {user_id}.")

    # 1. Call mock_server.py to get device data
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # CALLING YOUR MOCK SERVER
            response = await client.get(MOCK_SERVER_URL)
            response.raise_for_status()
            
            # We get a *single* WeeklyMetric object, as per your mock_server.py
            device_data_dict = response.json()
            device_data = WeeklyMetric(**device_data_dict)

    except httpx.RequestError as e:
        print(f"ERROR: Could not connect to mock server at {MOCK_SERVER_URL}. {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The mock device data service is currently unavailable. Please try again later."
        )
    except Exception as e:
        print(f"ERROR: Failed to parse mock data. {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process device data: {e}")
    
    # 2. Call `create_daily_record` to merge and save to 'daily_records'
    new_record = await create_daily_record(
        user_id=user_id,
        checkin_data=checkin_data,
        device_data=device_data
    )
    
    # 3. Also update the user's main weight in their 'users' profile
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"body_weight_kg": checkin_data.body_weight_kg}}
    )
    
    return new_record

@app.get(
    "/api/v1/user/checkins",
    response_model=List[MergedDailyRecord],
    summary="Get User's Check-in History"
)
async def get_user_checkins(user_id: str = Depends(get_patient_user)):
    """
    Fetches the check-in history for the authenticated patient from 'daily_records'.
    """
    records = []
    cursor = records_collection.find({"user_id": user_id}).sort("date", -1)
    async for record in cursor:
        records.append(record)
    return records


# --- 9. Doctor Endpoints (Requires 'doctor' role) ---

@app.get(
    "/api/v1/doctor/patients/{patient_id}/profile",
    response_model=UserProfile,
    summary="Get Patient Profile (Doctor)"
)
async def get_patient_profile_for_doctor(patient_id: str, doctor_id: str = Depends(get_doctor_user)):
    """
    Fetches a specific patient's profile from 'users'.
    """
    print(f"[DOCTOR] Doctor {doctor_id} is accessing profile for patient {patient_id}.")
    profile = await users_collection.find_one({"_id": patient_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    return profile

@app.get(
    "/api/v1/doctor/patients/{patient_id}/checkins",
    response_model=List[MergedDailyRecord],
    summary="Get Patient Check-ins (Doctor)"
)
async def get_patient_checkins_for_doctor(patient_id: str, doctor_id: str = Depends(get_doctor_user)):
    """
    Fetches a specific patient's check-in history from 'daily_records'.
    """
    print(f"[DOCTOR] Doctor {doctor_id} is accessing check-ins for patient {patient_id}.")
    records = []
    cursor = records_collection.find({"user_id": patient_id}).sort("date", -1)
    async for record in cursor:
        records.append(record)
    return records

@app.get(
    "/api/v1/doctor/patients/{patient_id}/analyze",
    response_model=AgentAnalysisResponse,
    summary="Run Agent Analysis (Doctor)"
)
async def analyze_patient_data(patient_id: str, doctor_id: str = Depends(get_doctor_user)):
    """
    This endpoint:
    1. Fetches the patient's profile from 'users'.
    2. Fetches all their records from 'daily_records'.
    3. Bundles it all, converts to a JSON string, and sends to `evaluate`.
    """
    print(f"[DOCTOR] Doctor {doctor_id} requested analysis for patient {patient_id}.")
    
    # 1. Get Profile
    profile = await users_collection.find_one({"_id": patient_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    # 2. Get All Daily Records
    records_cursor = records_collection.find({"user_id": patient_id})
    records = await records_cursor.to_list(length=100) # Get up to 100 records
    
    # --- Custom JSON Encoder to handle 'date' and 'ObjectId' ---
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (date, timedelta)):
                return obj.isoformat()
            if isinstance(obj, ObjectId):
                return str(obj)
            return json.JSONEncoder.default(self, obj)

    # 3. Bundle data for the agent
    # We must convert it to a JSON string for the prompt
    data_for_agent = {
        "baseline_profile": profile,
        "daily_records": records
    }
    data_string = json.dumps(data_for_agent, cls=CustomEncoder, indent=2)
    
    # 4. Call the evaluate function
    analysis_result_text = evaluate(data_string)
    
    return AgentAnalysisResponse(
        patient_id=patient_id,
        analysis_text=analysis_result_text
    )

# --- 10. Server Runner ---

if __name__ == "__main__":
    """
    This allows you to run the server directly by running
    `python main.py` in your terminal.
    It runs on port 8000.
    """
    print("--- Starting Main App FastAPI server on http://127.0.0.1:8000 ---")
    print("View API docs at http://127.0.0.1:8000/docs")
    print("Login as a DOCTOR: (doctor@example.com / doctorpass)")
    print("---")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)