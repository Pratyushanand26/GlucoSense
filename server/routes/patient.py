"""Patient routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from ..models import UserProfile, DailyCheckIn, MergedDailyRecord, HealthSummary
from ..auth import get_patient_user
from ..database import users_collection, records_collection
from ..health_service import create_daily_record, fetch_device_data, calculate_health_summary
from ..ai_service import generate_quick_insight

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
