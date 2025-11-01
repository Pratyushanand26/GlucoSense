from typing import List
from fastapi import APIRouter, Depends, HTTPException
from ..models import UserProfile, DailyCheckIn, MergedDailyRecord, HealthSummary, AgentAnalysisResponse, RecommendationsResponse
from ..auth import get_patient_user
from ..database import users_collection, records_collection
from ..health_service import create_daily_record, get_user_records, calculate_health_summary
from ..ai_service import generate_quick_insight, analyze_patient_health, generate_recommendations, disease_specific_analysis
from ..health_service import fetch_device_data

router = APIRouter(prefix="/api/v1/user", tags=["Patient"])

@router.get("/profile", response_model=UserProfile)
async def get_profile(user_id: str = Depends(get_patient_user)):
    """Get patient profile"""
    profile = await users_collection.find_one({"_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/profile", response_model=UserProfile)
async def update_profile(profile_data: UserProfile, user_id: str = Depends(get_patient_user)):
    """Update patient profile"""
    if profile_data.id != user_id:
        raise HTTPException(status_code=403, detail="Cannot update another user's profile")
    
    update_data = profile_data.dict(by_alias=False, exclude={"id"})
    await users_collection.update_one({"_id": user_id}, {"$set": update_data})
    
    updated = await users_collection.find_one({"_id": user_id})
    return updated

@router.post("/checkin", response_model=MergedDailyRecord)
async def submit_checkin(checkin_data: DailyCheckIn, user_id: str = Depends(get_patient_user)):
    """Submit daily check-in"""
    print(f"[CHECKIN] Patient {user_id}")
    
    device_data = await fetch_device_data()
    new_record = await create_daily_record(user_id, checkin_data, device_data)
    
    await users_collection.update_one(
        {"_id": user_id},
        {"$set": {"body_weight_kg": checkin_data.body_weight_kg}}
    )
    
    return new_record

@router.get("/checkins", response_model=List[MergedDailyRecord])
async def get_checkins(user_id: str = Depends(get_patient_user)):
    """Get check-in history"""
    records = []
    cursor = records_collection.find({"user_id": user_id}).sort("date", -1)
    async for record in cursor:
        records.append(record)
    return records

@router.get("/summary", response_model=HealthSummary)
async def get_summary(user_id: str = Depends(get_patient_user)):
    """Get health summary statistics (NEW API)"""
    return await calculate_health_summary(user_id)

@router.get("/latest-insight")
async def get_insight(user_id: str = Depends(get_patient_user)):
    """Get AI insight from latest check-in (NEW API)"""
    cursor = records_collection.find({"user_id": user_id}).sort("date", -1).limit(1)
    records = await cursor.to_list(length=1)
    
    if not records:
        raise HTTPException(status_code=404, detail="No check-in data found")
    
    latest = records[0]
    insight = await generate_quick_insight(latest)  # ✅ FIXED: Added await
    
    return {"date": latest['date'], "insight": insight}

@router.get("/analyze", response_model=AgentAnalysisResponse)
async def analyze_my_health(user_id: str = Depends(get_patient_user)):
    """Get AI analysis of your own health data (FREE)"""
    print(f"[PATIENT] {user_id} analyzing own health")
    
    profile = await users_collection.find_one({"_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    records = await get_user_records(user_id)
    if not records:
        raise HTTPException(status_code=404, detail="No check-in data for analysis. Submit at least one check-in first.")
    
    analysis = await analyze_patient_health(profile, records)
    return AgentAnalysisResponse(patient_id=user_id, analysis_text=analysis)

@router.get("/recommend", response_model=RecommendationsResponse)
async def get_my_recommendations(user_id: str = Depends(get_patient_user)):
    """Get AI recommendations for your health (FREE)"""
    print(f"[PATIENT] {user_id} requesting recommendations")
    
    profile = await users_collection.find_one({"_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    records = await get_user_records(user_id)
    if not records:
        raise HTTPException(status_code=404, detail="No check-in data available")
    
    # First analyze, then recommend
    evaluation = await analyze_patient_health(profile, records)
    recommendations = await generate_recommendations(profile, records, evaluation)
    
    return RecommendationsResponse(
        patient_id=user_id,
        evaluation=evaluation,
        recommendations=recommendations
    )

@router.get("/disease-specific")
async def get_disease_specific_analysis(user_id: str = Depends(get_patient_user)):
    """Get disease-specific AI analysis and recommendations (FREE)"""
    print(f"[PATIENT] {user_id} requesting disease-specific analysis")
    
    profile = await users_collection.find_one({"_id": user_id})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    records = await get_user_records(user_id)
    if not records:
        raise HTTPException(status_code=404, detail="No check-in data available")
    
    # Run disease-specific analysis using Disease_prompt
    analysis = await disease_specific_analysis(profile, records)
    
    return {
        "patient_id": user_id,
        "disease_specific_analysis": analysis
    }