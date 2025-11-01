# AI/LLM integration logic
"""AI/LLM integration service"""
import json
from datetime import date, datetime, timedelta
from bson import ObjectId
import google.generativeai as genai
from .config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

class CustomEncoder(json.JSONEncoder):
    """JSON encoder for date and ObjectId"""
    def default(self, obj):
        if isinstance(obj, (date, datetime, timedelta)):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def analyze_patient_health(baseline_profile: dict, daily_records: list) -> str:
    """Analyze patient health data using Gemini AI"""
    if not GEMINI_API_KEY:
        return "Error: AI model not configured"
    
    try:
        client = genai.GenerativeModel(model_name="gemini-2.5-pro")
        
        prompt = """
# HEALTH DATA EVALUATION SYSTEM

You are an AI health analyst combining medical knowledge and statistical expertise.

=== EVALUATION METHODOLOGY ===
1. TREND ANALYSIS: Compare current vs previous weeks, identify deviations
2. CORRELATION ASSESSMENT: Cross-reference multiple metrics
3. RED FLAGS: HR >100/<40 bpm, SpO₂ <92%, illness >7 days, HRV drop >30%
4. CONTEXT: Consider illness recovery, medications, age baselines

=== OUTPUT FORMAT ===

**STATUS: [NORMAL / CONSULT RECOMMENDED]**

**HEALTH CHECK SUMMARY**

*Evaluation Period:* [Date Range]
*Current Status:* [One-line summary]

**What We're Seeing:**
[2-3 paragraphs explaining trends in accessible language]

**Key Observations:**

✓ **Going Well:**
- [Positive findings]

⚠️ **Worth Noting:**
- [Changes but not urgent]

🔴 **Needs Attention:** (if applicable)
- [Concerns requiring consultation]

**Recommendations:**

*Immediate Actions:*
- Sleep: [specific suggestion]
- Hydration: [specific suggestion]
- Movement: [specific suggestion]

*Monitoring & Follow-up:*
1. [Tracking recommendation]

*Professional Consultation:* (if needed)
- [When to contact doctor]

**When to Seek Care:**
[Specific criteria]

=== SAFEGUARDS ===
- NEVER diagnose conditions
- Frame as observations, not diagnoses
- This is monitoring support, not medical advice

Now analyze:
"""
        
        data_for_agent = {
            "baseline_profile": baseline_profile,
            "daily_records": daily_records
        }
        data_string = json.dumps(data_for_agent, cls=CustomEncoder, indent=2)
        full_prompt = prompt + "\n\n" + data_string
        
        response = client.generate_content(full_prompt)
        return response.text
    
    except Exception as e:
        print(f"AI Error: {e}")
        return f"Error: AI analysis failed - {e}"

def generate_quick_insight(latest_record: dict) -> str:
    """Generate quick insight from latest check-in"""
    if not GEMINI_API_KEY:
        return "Quick insights unavailable"
    
    try:
        client = genai.GenerativeModel(model_name="gemini-2.5-pro")
        prompt = f"""
Provide a brief 2-3 sentence health insight based on this day's data.
Focus on what's notable and one actionable tip. Keep it friendly.

Data: {json.dumps(latest_record, cls=CustomEncoder)}
"""
        response = client.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Unable to generate insight"