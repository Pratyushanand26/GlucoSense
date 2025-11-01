# Pydantic models for the server
"""All Pydantic models"""
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, conint, EmailStr
import uuid

# === Baseline Profile ===
class MedicalHistory(BaseModel):
    chronic_conditions: List[str] = Field(default_factory=list)
    past_surgeries: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    known_allergies: List[str] = Field(default_factory=list)

class FamilyHistory(BaseModel):
    heart_disease: bool = False
    diabetes: bool = False
    cancer: bool = False
    other_hereditary_conditions: List[str] = Field(default_factory=list)

class LifestyleFactors(BaseModel):
    smoking_status: str
    alcohol_consumption: str
    exercise_habits: str

# === Auth ===
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    age: int
    height_cm: float
    sex: str
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

# === User Profile ===
class UserProfile(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr
    age: int
    height_cm: float
    sex: str
    body_weight_kg: Optional[float] = None
    medical_history: MedicalHistory
    family_history: FamilyHistory
    lifestyle_factors: LifestyleFactors

# === Device Data ===
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
    date: date
    heart_rate: HeartRate
    hrv: HRV
    sleep: Sleep
    activity: PhysicalActivity
    spo2: SpO2
    skin_temp: SkinTemperature

# === Check-in ===
class Coordinates(BaseModel):
    latitude: float
    longitude: float

class IllnessReport(BaseModel):
    present: bool
    description: Optional[str] = None
    duration_days: Optional[int] = None

class DailyCheckIn(BaseModel):
    body_weight_kg: float
    illness_symptoms: IllnessReport
    energy_level: conint(ge=0, le=10)
    muscle_soreness: conint(ge=0, le=10)
    mood_state: conint(ge=0, le=10)
    location_coordinates: Optional[Coordinates] = None
    additional_notes: Optional[str] = None

class MergedDailyRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    date: date
    checkin_data: DailyCheckIn
    device_data: WeeklyMetric

# === Analysis ===
class AgentAnalysisResponse(BaseModel):
    patient_id: str
    analysis_text: str

class HealthSummary(BaseModel):
    total_checkins: int
    date_range: dict
    average_metrics: dict
    latest_weight_kg: Optional[float] = None
    illness_count: int

class RecommendationsResponse(BaseModel):
    patient_id: str
    evaluation: str
    recommendations: str

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
    date: date
    heart_rate: HeartRate
    hrv: HRV
    sleep: Sleep
    activity: PhysicalActivity
    spo2: SpO2
    skin_temp: SkinTemperature