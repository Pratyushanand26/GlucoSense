from typing import List
from fastapi import APIRouter, Depends, HTTPException
from ..models import UserProfile, DailyCheckIn, MergedDailyRecord, HealthSummary, AgentAnalysisResponse, RecommendationsResponse
from ..auth import get_patient_user
from ..database import users_collection, records_collection
from ..health_service import create_daily_record, get_user_records, calculate_health_summary
from ..ai_service import generate_quick_insight, analyze_patient_health, generate_recommendations, disease_specific_analysis
from ..health_service import fetch_device_data
from datetime import date
import random
from ..models import WeeklyMetric

stored_weekly_data: List[WeeklyMetric] = []

router = APIRouter(prefix="/api/v1/user", tags=["Patient"])

def get_base_metrics():
    """Generate random base metrics"""
    return {
        "base_resting_hr": random.randint(60, 75),
        "base_hrv": random.randint(30, 50),
        "base_spo2": random.uniform(96.0, 98.0),
        "base_temp_dev": random.uniform(-0.5, 0.5),
        "base_steps": random.randint(4000, 7000)
    }

def generate_weekly_data_mock(base_metrics: dict) -> WeeklyMetric:
    """Generate mock weekly data"""
    from ..models import HeartRate, HRV, Sleep, PhysicalActivity, SpO2, SkinTemperature
    
    current_date = date.today()
    resting_hr = base_metrics["base_resting_hr"] + random.randint(-5, 5)
    
    return WeeklyMetric(
        date=current_date,
        heart_rate=HeartRate(
            resting_hr=resting_hr,
            average_weekly_hr=resting_hr + random.randint(10, 25)
        ),
        hrv=HRV(average_hrv=base_metrics["base_hrv"] + random.randint(-7, 7)),
        sleep=Sleep(sleep_duration_hours=round(random.uniform(6.0, 8.5), 1)),
        activity=PhysicalActivity(
            steps=max(1000, base_metrics["base_steps"] + random.randint(-2000, 3000)),
            calories_burned=int(base_metrics["base_steps"] * 0.04) + random.randint(100, 400)
        ),
        spo2=SpO2(
            average_spo2=max(92.0, round(base_metrics["base_spo2"] + random.uniform(-2.0, 0.5), 1))
        ),
        skin_temp=SkinTemperature(
            deviation_celsius=round(base_metrics["base_temp_dev"] + random.uniform(-0.3, 0.3), 2)
        )
    )

@router.get("/mock/weekly-summary", response_model=WeeklyMetric)
async def get_mock_weekly_summary():
    """Generate mock device data (replaces mock_server)"""
    base_metrics = get_base_metrics()
    return generate_weekly_data_mock(base_metrics)

@router.post("/mock/set-weekly-summary")
async def set_weekly_summary(data: WeeklyMetric):
    """Store mock device data temporarily"""
    stored_weekly_data.append(data)
    return {"message": "Mock health data stored"}

@router.get("/mock/get-weekly-summary")
async def get_and_clear_weekly_summary():
    """Fetch and clear latest mock data"""
    if not stored_weekly_data:
        return None
    return stored_weekly_data.pop()


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

@router.delete("/checkins/{record_id}")
async def delete_checkin(record_id: str, user_id: str = Depends(get_patient_user)):
    """Delete a specific check-in record"""
    result = await records_collection.delete_one({"_id": record_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found or unauthorized")
    return {"message": "Check-in deleted successfully"}

@router.get("/checkins/{record_id}", response_model=MergedDailyRecord)
async def get_single_checkin(record_id: str, user_id: str = Depends(get_patient_user)):
    """Get a specific check-in by ID"""
    record = await records_collection.find_one({"_id": record_id, "user_id": user_id})
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record