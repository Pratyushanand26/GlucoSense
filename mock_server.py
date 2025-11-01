import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import random
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

app = FastAPI(
    title="Health Data API",
    description="Mock and temporary storage API for health data.",
    version="2.2.0"
)

# --- Enable CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
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

# --- Temporary in-memory list ---
stored_weekly_data: List[WeeklyMetric] = []

# --- Helper: Random data generator ---
def get_base_metrics():
    return {
        "base_resting_hr": random.randint(60, 75),
        "base_hrv": random.randint(30, 50),
        "base_spo2": random.uniform(96.0, 98.0),
        "base_temp_dev": random.uniform(-0.5, 0.5),
        "base_steps": random.randint(4000, 7000)
    }

def generate_weekly_data(base_metrics: dict) -> WeeklyMetric:
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

# --- 1️⃣ Mock GET endpoint ---
@app.get("/api/v1/health/weekly-summary", response_model=WeeklyMetric)
def get_mock_weekly_summary():
    base_metrics = get_base_metrics()
    return generate_weekly_data(base_metrics)

# --- 2️⃣ POST endpoint to store user data temporarily ---
@app.post("/api/v1/health/set-weekly-summary")
def set_weekly_summary(data: WeeklyMetric):
    stored_weekly_data.append(data)
    return {"message": "Health data stored temporarily!"}

# --- 3️⃣ GET endpoint to fetch latest posted data and clear it ---
@app.get("/api/v1/health/get-weekly-summary", response_model=Optional[WeeklyMetric])
def get_and_clear_weekly_summary():
    if not stored_weekly_data:
        return None
    latest = stored_weekly_data.pop()  # remove after returning
    return latest

# --- Run server ---
if __name__ == "__main__":
    print("--- Starting Health Data API on http://127.0.0.1:8001 ---")
    print("Docs available at: http://127.0.0.1:8001/docs")
    uvicorn.run("mock_server:app", host="127.0.0.1", port=8001, reload=True)
