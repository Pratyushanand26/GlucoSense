# Health data processing logic
"""Health data processing service"""
import uuid
import httpx
from datetime import date, datetime
from typing import List, Dict
from fastapi import HTTPException, status
from .config import MOCK_SERVER_URL
from .models import DailyCheckIn, WeeklyMetric, MergedDailyRecord
from .database import records_collection

async def create_daily_record(
    user_id: str, 
    checkin_data: DailyCheckIn, 
    device_data: WeeklyMetric
) -> MergedDailyRecord:
    """Merge check-in and device data, save to database"""
    print(f"[HEALTH] Creating record for user {user_id}")
    
    merged_record = MergedDailyRecord(
        _id=str(uuid.uuid4()),
        user_id=user_id,
        date=date.today(),
        checkin_data=checkin_data,
        device_data=device_data
    )
    
    record_dict = merged_record.dict(by_alias=True)
    
    # Convert dates for MongoDB
    if isinstance(record_dict['date'], date) and not isinstance(record_dict['date'], datetime):
        record_dict['date'] = datetime.combine(record_dict['date'], datetime.min.time())
    
    if 'device_data' in record_dict and isinstance(record_dict['device_data'].get('date'), date):
        if not isinstance(record_dict['device_data']['date'], datetime):
            record_dict['device_data']['date'] = datetime.combine(
                record_dict['device_data']['date'], datetime.min.time()
            )
    
    await records_collection.insert_one(record_dict)
    print(f"[HEALTH] Saved record {merged_record.id}")
    return merged_record

async def fetch_device_data() -> WeeklyMetric:
    """Fetch data from mock device server"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(MOCK_SERVER_URL)
            response.raise_for_status()
            device_data_dict = response.json()
            return WeeklyMetric(**device_data_dict)
    except httpx.RequestError as e:
        print(f"ERROR: Device server unavailable - {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Device service unavailable"
        )
    except Exception as e:
        print(f"ERROR: Failed to parse device data - {e}")
        raise HTTPException(status_code=500, detail=f"Device data error: {e}")

async def get_user_records(user_id: str, limit: int = 100) -> List[dict]:
    """Fetch all records for a user"""
    cursor = records_collection.find({"user_id": user_id}).sort("date", -1).limit(limit)
    return await cursor.to_list(length=limit)

async def calculate_health_summary(user_id: str) -> Dict:
    """Calculate summary statistics"""
    records = await get_user_records(user_id)
    
    if not records:
        return {
            "total_checkins": 0,
            "date_range": {},
            "average_metrics": {},
            "latest_weight_kg": None,
            "illness_count": 0
        }
    
    total = len(records)
    avg_hr = sum(r['device_data']['heart_rate']['resting_hr'] for r in records) / total
    avg_sleep = sum(r['device_data']['sleep']['sleep_duration_hours'] for r in records) / total
    avg_steps = sum(r['device_data']['activity']['steps'] for r in records) / total
    avg_energy = sum(r['checkin_data']['energy_level'] for r in records) / total
    avg_mood = sum(r['checkin_data']['mood_state'] for r in records) / total
    
    dates = [r['date'] for r in records]
    
    return {
        "total_checkins": total,
        "date_range": {
            "earliest": min(dates).isoformat() if dates else None,
            "latest": max(dates).isoformat() if dates else None
        },
        "average_metrics": {
            "resting_heart_rate": round(avg_hr, 1),
            "sleep_hours": round(avg_sleep, 1),
            "daily_steps": round(avg_steps, 0),
            "energy_level": round(avg_energy, 1),
            "mood_state": round(avg_mood, 1)
        },
        "latest_weight_kg": records[0]['checkin_data']['body_weight_kg'],
        "illness_count": sum(1 for r in records if r['checkin_data']['illness_symptoms']['present'])
    }