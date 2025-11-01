from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

router = APIRouter()

class PatientProfile(BaseModel):
    id: str
    name: str
    age: int
    medical_history: List[str]

@router.get("/profile", response_model=PatientProfile)
async def get_patient_profile():
    # Mock patient profile data
    return PatientProfile(id="123", name="John Doe", age=30, medical_history=["Diabetes", "Hypertension"])

class HealthTrend(BaseModel):
    metric: str
    trend: List[float]

@router.get("/health-trends", response_model=List[HealthTrend])
async def get_health_trends():
    # Mock health trend data
    return [
        HealthTrend(metric="Heart Rate", trend=[70, 72, 75, 73, 71]),
        HealthTrend(metric="Sleep Duration", trend=[7.5, 8.0, 7.8, 7.6, 7.9])
    ]