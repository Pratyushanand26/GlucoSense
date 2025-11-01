import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import random
from typing import List
from datetime import date, timedelta
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Health Data Mock API",
    description="An API to provide mock health data summaries.",
    version="1.2.0"
)

# --- ADDED CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# --- Pydantic Models ---
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

# --- Helper Functions for Data Generation ---
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
    heart_rate_data = HeartRate(
        resting_hr=resting_hr,
        average_weekly_hr=resting_hr + random.randint(10, 25)
    )
    
    hrv_data = HRV(
        average_hrv=base_metrics["base_hrv"] + random.randint(-7, 7)
    )
    
    duration = round(random.uniform(6.0, 8.5), 1)
    sleep_data = Sleep(
        sleep_duration_hours=duration
    )
    
    steps = base_metrics["base_steps"] + random.randint(-2000, 3000)
    activity_data = PhysicalActivity(
        steps=max(1000, steps),
        calories_burned=int(steps * 0.04) + random.randint(100, 400)
    )
    
    spo2_data = SpO2(
        average_spo2=max(92.0, round(base_metrics["base_spo2"] + random.uniform(-2.0, 0.5), 1))
    )
    
    temp_data = SkinTemperature(
        deviation_celsius=round(base_metrics["base_temp_dev"] + random.uniform(-0.3, 0.3), 2)
    )
    
    return WeeklyMetric(
        date=current_date,
        heart_rate=heart_rate_data,
        hrv=hrv_data,
        sleep=sleep_data,
        activity=activity_data,
        spo2=spo2_data,
        skin_temp=temp_data
    )

# --- API Endpoint ---
@app.get(
    "/api/v1/health/weekly-summary",
    response_model=WeeklyMetric,
    summary="Get Mock Weekly Health Metric"
)
def get_weekly_summary():
    # --- BUG FIX: This was missing ---
    base_metrics = get_base_metrics()
    weekly_metric = generate_weekly_data(base_metrics)
    
    return weekly_metric

# --- Server Runner ---
if __name__ == "__main__":
    print("--- Starting Mock Device Data server on http://127.0.0.1:8001 ---")
    print("View API docs at http://127.0.0.1:8001/docs")
    print("Access weekly data at http://127.0.0.1:8001/api/v1/health/weekly-summary")
    print("---")
    # --- PORT CHANGED TO 8001 ---
    uvicorn.run("mock_server:app", host="127.0.0.1", port=8001, reload=True)