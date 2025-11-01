"""AI/LLM integration service using models folder logic"""
import json
from datetime import date, datetime, timedelta
from bson import ObjectId
import google.generativeai as genai
from .config import GEMINI_API_KEY

# Import prompts from models folder
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from models.prompt import Instruction, Recommendor_command, Disease_prompt

# Configure Gemini API key globally
genai.configure(api_key=GEMINI_API_KEY)


class CustomEncoder(json.JSONEncoder):
    """JSON encoder for date and ObjectId"""
    def default(self, obj):
        if isinstance(obj, (date, datetime, timedelta)):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def format_patient_data(baseline_profile: dict, daily_records: list) -> str:
    """Format patient data into readable text for AI"""
    profile_text = f"""
Patient Profile:
- Age: {baseline_profile.get('age')} years
- Sex: {baseline_profile.get('sex')}
- Height: {baseline_profile.get('height_cm')} cm
- Latest Weight: {baseline_profile.get('body_weight_kg', 'Not recorded')} kg

Medical History:
- Chronic Conditions: {', '.join(baseline_profile.get('medical_history', {}).get('chronic_conditions', [])) or 'None'}
- Current Medications: {', '.join(baseline_profile.get('medical_history', {}).get('current_medications', [])) or 'None'}
- Allergies: {', '.join(baseline_profile.get('medical_history', {}).get('known_allergies', [])) or 'None'}

Family History:
- Heart Disease: {'Yes' if baseline_profile.get('family_history', {}).get('heart_disease') else 'No'}
- Diabetes: {'Yes' if baseline_profile.get('family_history', {}).get('diabetes') else 'No'}
- Cancer: {'Yes' if baseline_profile.get('family_history', {}).get('cancer') else 'No'}

Lifestyle:
- Smoking: {baseline_profile.get('lifestyle_factors', {}).get('smoking_status', 'Unknown')}
- Alcohol: {baseline_profile.get('lifestyle_factors', {}).get('alcohol_consumption', 'Unknown')}
- Exercise: {baseline_profile.get('lifestyle_factors', {}).get('exercise_habits', 'Unknown')}
"""

    # Format weekly records
    records_text = "\nWeekly Health Data:\n"
    records_text += "| Week | Date | Rest HR | HRV | Sleep | Steps | Calories | SpO₂ | Skin Temp | Weight | Illness | Energy | Soreness | Mood |\n"
    records_text += "|------|------|---------|-----|-------|-------|----------|------|-----------|--------|---------|--------|----------|------|\n"

    for i, record in enumerate(daily_records[:8], 1):
        checkin = record.get('checkin_data', {})
        device = checkin.get('device_data', {})
        illness = checkin.get('illness_symptoms', {})

        illness_str = "No"
        if illness.get('present'):
            desc = illness.get('description', 'Yes')
            duration = illness.get('duration_days', '')
            illness_str = f"{desc} ({duration} days)" if duration else desc

        records_text += f"| {i} | {record.get('date', 'N/A')} | "
        records_text += f"{device.get('heart_rate', {}).get('resting_hr', 'N/A')} | "
        records_text += f"{device.get('hrv', {}).get('average_hrv', 'N/A')} | "
        records_text += f"{device.get('sleep', {}).get('sleep_duration_hours', 'N/A')} | "
        records_text += f"{device.get('activity', {}).get('steps', 'N/A')} | "
        records_text += f"{device.get('activity', {}).get('calories_burned', 'N/A')} | "
        records_text += f"{device.get('spo2', {}).get('average_spo2', 'N/A')} | "
        records_text += f"{device.get('skin_temp', {}).get('deviation_celsius', 'N/A')} | "
        records_text += f"{checkin.get('body_weight_kg', 'N/A')} | "
        records_text += f"{illness_str} | "
        records_text += f"{checkin.get('energy_level', 'N/A')}/10 | "
        records_text += f"{checkin.get('muscle_soreness', 'N/A')}/10 | "
        records_text += f"{checkin.get('mood_state', 'N/A')}/10 |\n"

    return profile_text + records_text


# ---------------- AI FUNCTIONS ---------------- #

async def analyze_patient_health(baseline_profile: dict, daily_records: list) -> str:
    """Analyze patient health using Gemini AI."""
    if not GEMINI_API_KEY:
        return "Error: AI model not configured"

    try:
        print('[AI] Evaluating patient health...')
        formatted_data = format_patient_data(baseline_profile, daily_records)
        full_prompt = Instruction.replace("{data}", formatted_data)

        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(full_prompt)

        print('[AI] Evaluation complete')
        return response.text.strip()

    except Exception as e:
        print(f"[AI] Error: {e}")
        return f"Error: AI analysis failed - {e}"


async def generate_recommendations(baseline_profile: dict, daily_records: list, evaluation_result: str) -> str:
    """Generate health recommendations using Gemini AI."""
    if not GEMINI_API_KEY:
        return "Error: AI model not configured"

    try:
        print('[AI] Generating recommendations...')
        formatted_data = format_patient_data(baseline_profile, daily_records)
        full_prompt = Recommendor_command.replace("{result}", evaluation_result).replace("{data}", formatted_data)

        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(full_prompt)

        print('[AI] Recommendations generated')
        return response.text.strip()

    except Exception as e:
        print(f"[AI] Error: {e}")
        return f"Error: Recommendation generation failed - {e}"


async def generate_quick_insight(latest_record: dict) -> str:
    """Generate quick health insight."""
    if not GEMINI_API_KEY:
        return "Quick insights unavailable"

    try:
        checkin = latest_record.get('checkin_data', {})
        device = checkin.get('device_data', {})

        prompt = f"""
Provide a brief 2–3 sentence friendly health insight based on today's data.
Focus on what's notable and give one actionable tip.

Today's Metrics:
- Heart Rate: {device.get('heart_rate', {}).get('resting_hr')} bpm
- Sleep: {device.get('sleep', {}).get('sleep_duration_hours')} hours
- Steps: {device.get('activity', {}).get('steps')}
- SpO₂: {device.get('spo2', {}).get('average_spo2')}%
- Energy Level: {checkin.get('energy_level')}/10
- Mood: {checkin.get('mood_state')}/10
- Illness: {'Yes - ' + checkin.get('illness_symptoms', {}).get('description', '') if checkin.get('illness_symptoms', {}).get('present') else 'No'}
"""

        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception as e:
        print("Error generating insight:", e)
        return "Unable to generate insight"


async def disease_specific_analysis(baseline_profile: dict, daily_records: list) -> str:
    """Disease-specific evaluation and recommendations."""
    if not GEMINI_API_KEY:
        return "Error: AI model not configured"

    try:
        print('[AI] Running disease-specific analysis...')
        formatted_data = format_patient_data(baseline_profile, daily_records)
        full_prompt = Disease_prompt.replace("{data}", formatted_data)

        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(full_prompt)

        print('[AI] Disease-specific analysis complete')
        return response.text.strip()

    except Exception as e:
        print(f"[AI] Error: {e}")
        return f"Error: Disease-specific analysis failed - {e}"
