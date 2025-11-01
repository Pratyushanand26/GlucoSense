"""Doctor routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from ..models import UserProfile, MergedDailyRecord, AgentAnalysisResponse, HealthSummary
from ..auth import get_doctor_user
from ..database import users_collection, records_collection
from ..health_service import get_user_records, calculate_health_summary
from ..ai_service import analyze_patient_health

router = APIRouter(prefix="/api/v1/doctor", tags=["Doctor"])

@router.get("/patients")
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    doctor_id: str = Depends(get_doctor_user)
):
    """List all patients with pagination (NEW API)"""
    cursor = users_collection.find({"role": "patient"}).skip(skip).limit(limit)
    patients = await cursor.to_list(length=limit)
    
    for p in patients:
        p.pop('hashed_password', None)
    
    total = await users_collection.count_documents({"role": "patient"})
    return {"patients": patients, "total": total, "skip": skip, "limit": limit}

@router.get("/patients/search")
async def search_patients(
    email: str = Query(None),
    age_min: int = Query(None, ge=0),
    age_max: int = Query(None, le=120),
    doctor_id: str = Depends(get_doctor_user)
):
    """Search patients by criteria (NEW API)"""
    query = {"role": "patient"}
    
    if email:
        query["email"] = {"$regex": email, "$options": "i"}
    
    if age_min or age_max:
        age_query = {}
        if age_min:
            age_query["$gte"] = age_min
        if age_max:
            age_query["$lte"] = age_max
        query["age"] = age_query
    
    cursor = users_collection.find(query).limit(50)
    patients = await cursor.to_list(length=50)
    
    for p in patients:
        p.pop('hashed_password', None)
    
    return {"patients": patients, "count": len(patients)}

@router.get("/patients/{patient_id}/profile", response_model=UserProfile)
async def get_patient_profile(patient_id: str, doctor_id: str = Depends(get_doctor_user)):
    """Get patient profile"""
    print(f"[DOCTOR] {doctor_id} viewing patient {patient_id}")
    profile = await users_collection.find_one({"_id": patient_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Patient not found")
    return profile

@router.get("/patients/{patient_id}/checkins", response_model=List[MergedDailyRecord])
async def get_patient_checkins(patient_id: str, doctor_id: str = Depends(get_doctor_user)):
    """Get patient check-ins"""
    records = []
    cursor = records_collection.find({"user_id": patient_id}).sort("date", -1)
    async for record in cursor:
        records.append(record)
    return records

@router.get("/patients/{patient_id}/summary", response_model=HealthSummary)
async def get_patient_summary(patient_id: str, doctor_id: str = Depends(get_doctor_user)):
    """Get patient health summary (NEW API)"""
    return await calculate_health_summary(patient_id)

@router.get("/patients/{patient_id}/analyze", response_model=AgentAnalysisResponse)
async def analyze_patient(patient_id: str, doctor_id: str = Depends(get_doctor_user)):
    """Run AI analysis on patient"""
    print(f"[DOCTOR] {doctor_id} analyzing {patient_id}")
    
    profile = await users_collection.find_one({"_id": patient_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    records = await get_user_records(patient_id)
    if not records:
        raise HTTPException(status_code=404, detail="No data for analysis")
    
    analysis = analyze_patient_health(profile, records)
    return AgentAnalysisResponse(patient_id=patient_id, analysis_text=analysis)

# Add this new endpoint after the analyze endpoint
@router.get("/patients/{patient_id}/recommend")
async def recommend_for_patient(patient_id: str, doctor_id: str = Depends(get_doctor_user)):
    """Generate AI recommendations for patient"""
    print(f"[DOCTOR] {doctor_id} getting recommendations for {patient_id}")
    
    profile = await users_collection.find_one({"_id": patient_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    records = await get_user_records(patient_id)
    if not records:
        raise HTTPException(status_code=404, detail="No data available")
    
    # First analyze, then recommend
    evaluation = await analyze_patient_health(profile, records)
    recommendations = await generate_recommendations(profile, records, evaluation)
    
    return {
        "patient_id": patient_id,
        "evaluation": evaluation,
        "recommendations": recommendations
    }