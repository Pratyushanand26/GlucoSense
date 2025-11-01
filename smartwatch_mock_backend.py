import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import random
from typing import List
from datetime import date, timedelta

app = FastAPI(
    title="Health Data Mock API",
    description="An API to provide mock health data summaries.",
    version="1.2.0"  # Incremented version
)

# --- Pydantic Models ---
# Models are used by FastAPI to validate data and auto-generate documentation.

class HeartRate(BaseModel):
    """Model for daily heart rate data."""
    resting_hr: int
    average_daily_hr: int

class HRV(BaseModel):
    """Model for daily Heart Rate Variability."""
    average_hrv: int

class Sleep(BaseModel):
    """
    Model for daily sleep data.
    'sleep_quality_score' has been removed.
    'time_in_bed_hours' has been removed.
    """
    sleep_duration_hours: float

class PhysicalActivity(BaseModel):
    """
    Model for daily physical activity.
    'active_minutes' has been removed.
    """
    steps: int
    calories_burned: int

class SpO2(BaseModel):
    """Model for daily Blood Oxygen Saturation."""
    average_spo2: float

# --- REMOVED Stress Model ---
# class Stress(BaseModel):
#     """Model for daily stress level."""
#     average_stress_level: int # A score, e.g., 1-100

class SkinTemperature(BaseModel):
    """Model for nightly skin temperature deviation."""
    deviation_celsius: float # e.g., +0.2, -0.1

class DailyMetric(BaseModel):
    """A container for all metrics recorded on a single day."""
    # --- REMOVED day_index ---
    # day_index: int # 0 = 6 days ago, 6 = today
    date: date
    heart_rate: HeartRate
    hrv: HRV
    sleep: Sleep
    activity: PhysicalActivity
    spo2: SpO2
    # --- REMOVED stress ---
    # stress: Stress
    skin_temp: SkinTemperature

class WeeklyHealthSummary(BaseModel):
    """
    The main response model for a weekly summary.
    NOTE: This is no longer used by the primary endpoint,
    but is kept for potential future use.
    """
    user_id: str
    week_start_date: date
    week_end_date: date
    daily_metrics: List[DailyMetric]

# --- Helper Functions for Data Generation ---

def get_base_metrics():
    """Generates a set of base metrics for a user."""
    return {
        "base_resting_hr": random.randint(60, 75),
        "base_hrv": random.randint(30, 50),
        "base_spo2": random.uniform(96.0, 98.0),
        # --- REMOVED base_stress ---
        # "base_stress": random.randint(20, 40),
        "base_temp_dev": random.uniform(-0.5, 0.5),
        "base_steps": random.randint(4000, 7000)
    }

def generate_daily_data(base_metrics: dict) -> DailyMetric:
    """
    Generates randomized daily data for a single day based on base metrics.
    'day_index' parameter has been removed.
    """
    # --- UPDATED current_date logic ---
    current_date = date.today()
    
    # 1. Heart Rate
    resting_hr = base_metrics["base_resting_hr"] + random.randint(-5, 5)
    heart_rate_data = HeartRate(
        resting_hr=resting_hr,
        average_daily_hr=resting_hr + random.randint(10, 25)
    )
    
    # 2. HRV
    hrv_data = HRV(
        average_hrv=base_metrics["base_hrv"] + random.randint(-7, 7)
    )
    
    # 3. Sleep (Removed quality & time in bed)
    duration = round(random.uniform(6.0, 8.5), 1)
    sleep_data = Sleep(
        sleep_duration_hours=duration
    )
    
    # 4. Physical Activity (Removed active minutes)
    steps = base_metrics["base_steps"] + random.randint(-2000, 3000)
    activity_data = PhysicalActivity(
        steps=max(1000, steps), # Ensure steps are not ridiculously low
        calories_burned=int(steps * 0.04) + random.randint(100, 400) # Simple calorie estimation
    )
    
    # 5. SpO2
    spo2_data = SpO2(
        average_spo2=max(92.0, round(base_metrics["base_spo2"] + random.uniform(-2.0, 0.5), 1))
    )
    
    # --- REMOVED Stress generation ---
    # 6. Stress
    # stress_data = Stress(
    #     average_stress_level=max(1, min(100, base_metrics["base_stress"] + random.randint(-15, 20)))
    # )
    
    # 7. Skin Temperature
    temp_data = SkinTemperature(
        deviation_celsius=round(base_metrics["base_temp_dev"] + random.uniform(-0.3, 0.3), 2)
    )
    
    return DailyMetric(
        # --- REMOVED day_index ---
        # day_index=day_index,
        date=current_date,
        heart_rate=heart_rate_data,
        hrv=hrv_data,
        sleep=sleep_data,
        activity=activity_data,
        spo2=spo2_data,
        # --- REMOVED stress ---
        # stress=stress_data,
        skin_temp=temp_data
    )

# --- API Endpoint (Updated to Daily) ---

@app.get(
    "/api/v1/health/daily-summary",  # <-- CHANGED Path
    response_model=DailyMetric,      # <-- CHANGED Response Model
    summary="Get Mock Daily Health Metric", # <-- CHANGED Summary
    description="Returns a single day of mock health metrics for 'today'. " # <-- CHANGED Desc
                "Regenerates new random data on every call."
)
def get_daily_summary():
    """
    This endpoint generates and returns a single, randomized
    daily health metric summary for a mock user for 'today'.
    """
    # Generate base metrics for consistency
    base_metrics = get_base_metrics()
    
    # --- UPDATED call to remove day_index ---
    # We pass day_index=6, which corresponds to "today"
    daily_metric = generate_daily_data(base_metrics)
    
    return daily_metric

# --- Server Runner ---

if __name__ == "__main__":
    """
    This allows you to run the server directly by running
    `python main.py` in your terminal.
    """
    print("Starting FastAPI server at http://127.0.0.1:8000")
    print("View API docs at http://127.0.0.1:8000/docs")
    print("Access daily data at http://127.0.0.1:8000/api/v1/health/daily-summary")
    uvicorn.run(app, host="127.0.0.1", port=8000)



