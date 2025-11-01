from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()

class PatientSummary(BaseModel):
    id: str
    name: str
    recent_checkups: List[str]

@router.get("/patients", response_model=List[PatientSummary])
async def get_patients():
    # Mock list of patients
    return [
        PatientSummary(id="123", name="John Doe", recent_checkups=["2025-10-01", "2025-10-15"]),
        PatientSummary(id="124", name="Jane Smith", recent_checkups=["2025-09-20", "2025-10-10"])
    ]

class AggregatedStats(BaseModel):
    total_patients: int
    average_age: float
    common_conditions: Dict[str, int]

@router.get("/aggregated-stats", response_model=AggregatedStats)
async def get_aggregated_stats():
    # Mock aggregated statistics
    return AggregatedStats(
        total_patients=150,
        average_age=45.3,
        common_conditions={"Diabetes": 50, "Hypertension": 40}
    )